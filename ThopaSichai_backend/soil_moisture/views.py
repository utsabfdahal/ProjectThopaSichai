import logging
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from .models import SoilMoisture, Motor, SystemMode, ThresholdConfig, Sensor
from .serializers import (
    SoilMoistureSerializer, MotorSerializer, SystemModeSerializer,
    ThresholdConfigSerializer, BulkMotorControlSerializer,
    SystemStatusSerializer, DashboardStatsSerializer, HealthCheckSerializer
)
from .motor_logic import get_motor_state

logger = logging.getLogger('soil_moisture')


def create_response(success=True, data=None, message=None, errors=None, status_code=status.HTTP_200_OK):
    """Create a structured response format for all API endpoints."""
    response_data = {'success': success}
    if data is not None:
        response_data['data'] = data
    if message:
        response_data['message'] = message
    if errors:
        response_data['errors'] = errors
    return Response(response_data, status=status_code)


@extend_schema(
    parameters=[
        OpenApiParameter(name='page', type=int, description='Page number (default: 1)'),
        OpenApiParameter(name='page_size', type=int, description='Items per page (default: 100, max: 1000)'),
    ],
    responses={200: SoilMoistureSerializer(many=True)},
    description="Retrieve all soil moisture records with pagination"
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def list_soil_moisture(request):
    """GET endpoint to retrieve all SoilMoisture records. No authentication required."""
    try:
        logger.info(f"GET request received from IP: {request.META.get('REMOTE_ADDR')}")
        
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 100))
        
        if page < 1 or page_size < 1 or page_size > 1000:
            return create_response(
                success=False,
                errors={'pagination': 'Invalid pagination parameters'},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        offset = (page - 1) * page_size
        queryset = SoilMoisture.objects.all()
        total_count = queryset.count()
        records = queryset[offset:offset + page_size]
        
        serializer = SoilMoistureSerializer(records, many=True)
        
        logger.info(f"Retrieved {len(records)} records (page {page}, total: {total_count})")
        
        return create_response(
            success=True,
            data={
                'records': serializer.data,
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total_count': total_count,
                    'total_pages': (total_count + page_size - 1) // page_size if total_count > 0 else 0
                }
            },
            message='Records retrieved successfully'
        )
    
    except Exception as e:
        logger.error(f"Error retrieving SoilMoisture records: {str(e)}", exc_info=True)
        return create_response(
            success=False,
            errors={'detail': 'An error occurred while retrieving records'},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    request=SoilMoistureSerializer,
    responses={201: OpenApiResponse(description="Data received and motor updated if in AUTOMATIC mode")},
    description="ESP32 sensor endpoint - receives soil moisture data. Auto-creates sensor if new nodeid."
)
@api_view(['POST'])
@csrf_exempt  # Exempt from CSRF for IoT devices
@authentication_classes([])
@permission_classes([AllowAny])
def receive_soil_moisture(request):
    """
    Endpoint for ESP32 to send soil moisture data. No authentication or CSRF required.
    Auto-creates Sensor if new nodeid arrives.
    In AUTOMATIC mode, will automatically control motor mapped to sensor.
    
    Flow:
    1. Sensor ESP32 sends: {"nodeid": "sensor_zone1", "value": 45.5}
    2. System auto-creates Sensor if nodeid is new
    3. Saves moisture reading linked to sensor
    4. If Motor exists for sensor and in AUTOMATIC mode: controls motor
    5. Motor controller ESP32 fetches /motorsinfo to see which motors to turn on/off
    """
    from .models import Sensor, Motor, SystemMode, ThresholdConfig
    
    logger.info(f"Received data from ESP32: {request.data}")
    
    # Get nodeid from request
    nodeid = request.data.get('nodeid')
    if not nodeid:
        return create_response(
            success=False,
            errors={'nodeid': 'This field is required'},
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # Auto-create sensor if it doesn't exist
    sensor, sensor_created = Sensor.objects.get_or_create(
        nodeid=nodeid,
        defaults={'name': f'Auto-created: {nodeid}'}
    )
    
    if sensor_created:
        logger.info(f"Auto-created new sensor: {nodeid}")
    
    # Add IP address and prepare data
    data = request.data.copy()
    if 'ip_address' not in data:
        data['ip_address'] = request.META.get('REMOTE_ADDR', 'unknown')
    
    serializer = SoilMoistureSerializer(data=data, context={'sensor': sensor})
    
    if serializer.is_valid():
        moisture_record = serializer.save(sensor=sensor)
        logger.info(f"Successfully saved data from nodeid: {nodeid}, value: {moisture_record.value}%")
        
        response_data = {
            "status": "ok",
            "message": "Data received successfully",
            "nodeid": nodeid,
            "sensor_created": sensor_created,
            "moisture_value": moisture_record.value
        }
        
        # Check if we're in AUTOMATIC mode
        try:
            current_mode = SystemMode.get_current_mode()
            
            if current_mode == 'AUTOMATIC':
                # Check if motor exists for this sensor
                try:
                    motor = sensor.motor  # OneToOne relationship
                    
                    # Get threshold config for this sensor (creates default if not exists)
                    threshold = ThresholdConfig.get_threshold(sensor)
                    
                    # Determine desired motor state based on sensor reading
                    motor_decision = get_motor_state(
                        moisture_value=moisture_record.value,
                        current_state=motor.state,
                        threshold=threshold
                    )
                    
                    desired_state = motor_decision['desired_state']
                    
                    # Update motor state if it changed
                    if motor.state != desired_state:
                        motor.state = desired_state
                        motor.save()
                        logger.info(f"AUTOMATIC mode: Motor '{motor.name}' (sensor={nodeid}) changed to {desired_state}")
                        response_data['motor_update'] = {
                            'motor_name': motor.name,
                            'sensor_nodeid': nodeid,
                            'new_state': desired_state,
                            'reason': motor_decision['reason']
                        }
                    else:
                        response_data['motor_update'] = {
                            'motor_name': motor.name,
                            'sensor_nodeid': nodeid,
                            'state': motor.state,
                            'reason': f'No change needed - {motor_decision["reason"]}'
                        }
                    
                    response_data['mode'] = 'AUTOMATIC'
                    response_data['threshold'] = threshold
                
                except Motor.DoesNotExist:
                    logger.warning(f"No motor found for sensor: {nodeid}")
                    response_data['motor_update'] = f'No motor configured for sensor: {nodeid}'
                    response_data['mode'] = 'AUTOMATIC'
            else:
                response_data['mode'] = 'MANUAL'
                response_data['motor_update'] = 'Manual mode - motors not automatically controlled'
        
        except Exception as e:
            logger.error(f"Error in automatic motor control: {str(e)}", exc_info=True)
            # Don't fail the request, just log the error
            response_data['motor_control_error'] = str(e)
        
        return Response(response_data, status=201)
    
    logger.warning(f"Validation errors: {serializer.errors}")
    return Response({"status": "error", "errors": serializer.errors}, status=400)


@extend_schema(
    parameters=[
        OpenApiParameter(name='nodeid', type=str, description='Filter by specific node ID'),
        OpenApiParameter(name='check_motor', type=bool, description='Include motor recommendation (default: true)'),
        OpenApiParameter(name='low_threshold', type=float, description='Low moisture threshold (default: 45.0)'),
        OpenApiParameter(name='high_threshold', type=float, description='High moisture threshold (default: 70.0)'),
        OpenApiParameter(name='current_motor_state', type=str, description='Current motor state for hysteresis (default: OFF)'),
    ],
    responses={200: SoilMoistureSerializer},
    description="Get latest soil moisture reading with optional motor state recommendation"
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def get_latest_sensor_data(request):
    """
    GET endpoint to retrieve the latest soil moisture reading.
    Optional query parameters:
    - nodeid: Filter by specific node ID
    - check_motor: If 'false', excludes motor state recommendation (default: 'true')
    - low_threshold: Custom low threshold (default: 30)
    - high_threshold: Custom high threshold (default: 70)
    - current_motor_state: Current motor state for hysteresis logic (default: 'OFF')
    """
    try:
        nodeid = request.query_params.get('nodeid', None)
        check_motor = request.query_params.get('check_motor', 'true').lower() == 'true'
        
        logger.info(f"GET latest sensor data request from IP: {request.META.get('REMOTE_ADDR')}, nodeid={nodeid}")
        
        # Build query
        queryset = SoilMoisture.objects.all()
        if nodeid:
            queryset = queryset.filter(nodeid=nodeid)
        
        # Get the latest record
        latest_record = queryset.order_by('-created_at').first()
        
        if not latest_record:
            return create_response(
                success=False,
                message='No sensor data found',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        serializer = SoilMoistureSerializer(latest_record)
        response_data = {
            'sensor_data': serializer.data
        }
        
        # If motor checking is requested, add motor state recommendation
        if check_motor:
            try:
                low_threshold = float(request.query_params.get('low_threshold', 45.0))
                high_threshold = float(request.query_params.get('high_threshold', 70.0))
                current_motor_state = request.query_params.get('current_motor_state', 'OFF').upper()
                
                if current_motor_state not in ['ON', 'OFF']:
                    current_motor_state = 'OFF'
                
                motor_decision = get_motor_state(
                    moisture_value=latest_record.value,
                    current_state=current_motor_state,
                    low_threshold=low_threshold,
                    high_threshold=high_threshold
                )
                response_data['motor_recommendation'] = motor_decision
                
                logger.info(f"Motor recommendation: {motor_decision['desired_state']}")
                
            except ValueError as e:
                logger.warning(f"Invalid threshold parameters: {str(e)}")
                return create_response(
                    success=False,
                    errors={'threshold': str(e)},
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        
        return create_response(
            success=True,
            data=response_data,
            message='Latest sensor data retrieved successfully'
        )
    
    except Exception as e:
        logger.error(f"Error retrieving latest sensor data: {str(e)}", exc_info=True)
        return create_response(
            success=False,
            errors={'detail': 'An error occurred while retrieving latest sensor data'},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ===============================
# MOTOR CONTROL ENDPOINTS
# ===============================

@extend_schema(
    request=MotorSerializer,
    responses={200: MotorSerializer(many=True), 201: MotorSerializer},
    description="List all motors (GET) or create a new motor (POST)"
)
@api_view(['GET', 'POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def list_create_motors(request):
    """
    GET: List all motors
    POST: Create a new motor
    """
    if request.method == 'GET':
        try:
            motors = Motor.objects.all()
            serializer = MotorSerializer(motors, many=True)
            return create_response(
                success=True,
                data={'motors': serializer.data},
                message='Motors retrieved successfully'
            )
        except Exception as e:
            logger.error(f"Error retrieving motors: {str(e)}", exc_info=True)
            return create_response(
                success=False,
                errors={'detail': 'An error occurred while retrieving motors'},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    elif request.method == 'POST':
        try:
            serializer = MotorSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Motor created: {serializer.data['name']}")
                return create_response(
                    success=True,
                    data={'motor': serializer.data},
                    message='Motor created successfully',
                    status_code=status.HTTP_201_CREATED
                )
            return create_response(
                success=False,
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error creating motor: {str(e)}", exc_info=True)
            return create_response(
                success=False,
                errors={'detail': 'An error occurred while creating motor'},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    request=MotorSerializer,
    responses={200: MotorSerializer, 204: OpenApiResponse(description="Motor deleted")},
    description="Get, update, or delete a specific motor"
)
@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([])
@permission_classes([AllowAny])
def motor_detail(request, motor_id):
    """
    GET: Retrieve a specific motor
    PUT: Update motor (including state change in manual mode)
    DELETE: Delete a motor
    """
    try:
        motor = Motor.objects.get(id=motor_id)
    except Motor.DoesNotExist:
        return create_response(
            success=False,
            errors={'detail': 'Motor not found'},
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = MotorSerializer(motor)
        return create_response(
            success=True,
            data={'motor': serializer.data},
            message='Motor retrieved successfully'
        )
    
    elif request.method == 'PUT':
        try:
            current_mode = SystemMode.get_current_mode()
            
            # If trying to change state, check if we're in manual mode
            if 'state' in request.data:
                if current_mode != 'MANUAL':
                    return create_response(
                        success=False,
                        errors={'detail': 'Cannot manually control motor state in AUTOMATIC mode. Switch to MANUAL mode first.'},
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
            
            serializer = MotorSerializer(motor, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Motor {motor_id} updated: {serializer.data}")
                return create_response(
                    success=True,
                    data={'motor': serializer.data},
                    message='Motor updated successfully'
                )
            return create_response(
                success=False,
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error updating motor: {str(e)}", exc_info=True)
            return create_response(
                success=False,
                errors={'detail': 'An error occurred while updating motor'},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    elif request.method == 'DELETE':
        try:
            motor.delete()
            logger.info(f"Motor {motor_id} deleted")
            return create_response(
                success=True,
                message='Motor deleted successfully',
                status_code=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            logger.error(f"Error deleting motor: {str(e)}", exc_info=True)
            return create_response(
                success=False,
                errors={'detail': 'An error occurred while deleting motor'},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    request=MotorSerializer,
    responses={200: MotorSerializer},
    description="Control motor state in MANUAL mode - set to ON or OFF"
)
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def control_motor(request, motor_id):
    """
    Convenience endpoint to directly control motor state in MANUAL mode.
    POST with {"state": "ON"} or {"state": "OFF"}
    """
    try:
        motor = Motor.objects.get(id=motor_id)
    except Motor.DoesNotExist:
        return create_response(
            success=False,
            errors={'detail': 'Motor not found'},
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    current_mode = SystemMode.get_current_mode()
    
    if current_mode != 'MANUAL':
        return create_response(
            success=False,
            errors={'detail': 'Cannot manually control motor in AUTOMATIC mode. Switch to MANUAL mode first.'},
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    state = request.data.get('state', '').upper()
    if state not in ['ON', 'OFF']:
        return create_response(
            success=False,
            errors={'state': 'State must be "ON" or "OFF"'},
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        motor.state = state
        motor.save()
        logger.info(f"Motor {motor_id} state changed to {state} (MANUAL mode)")
        
        serializer = MotorSerializer(motor)
        return create_response(
            success=True,
            data={'motor': serializer.data},
            message=f'Motor turned {state}'
        )
    except Exception as e:
        logger.error(f"Error controlling motor: {str(e)}", exc_info=True)
        return create_response(
            success=False,
            errors={'detail': 'An error occurred while controlling motor'},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ===============================
# SYSTEM MODE ENDPOINTS
# ===============================

@extend_schema(
    responses={200: SystemModeSerializer},
    description="Get current system mode (MANUAL or AUTOMATIC)"
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def get_system_mode(request):
    """Get current system mode (MANUAL or AUTOMATIC)."""
    try:
        mode_obj = SystemMode.objects.get_or_create(id=1, defaults={'mode': 'AUTOMATIC'})[0]
        serializer = SystemModeSerializer(mode_obj)
        return create_response(
            success=True,
            data={'system_mode': serializer.data},
            message='System mode retrieved successfully'
        )
    except Exception as e:
        logger.error(f"Error retrieving system mode: {str(e)}", exc_info=True)
        return create_response(
            success=False,
            errors={'detail': 'An error occurred while retrieving system mode'},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    request=SystemModeSerializer,
    responses={200: SystemModeSerializer},
    description="Set system mode to MANUAL or AUTOMATIC"
)
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def set_system_mode(request):
    """
    Set system mode to MANUAL or AUTOMATIC.
    POST with {"mode": "MANUAL"} or {"mode": "AUTOMATIC"}
    """
    mode = request.data.get('mode', '').upper()
    
    if mode not in ['MANUAL', 'AUTOMATIC']:
        return create_response(
            success=False,
            errors={'mode': 'Mode must be "MANUAL" or "AUTOMATIC"'},
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        mode_obj = SystemMode.set_mode(mode)
        logger.info(f"System mode changed to {mode}")
        
        serializer = SystemModeSerializer(mode_obj)
        return create_response(
            success=True,
            data={'system_mode': serializer.data},
            message=f'System mode set to {mode}'
        )
    except Exception as e:
        logger.error(f"Error setting system mode: {str(e)}", exc_info=True)
        return create_response(
            success=False,
            errors={'detail': 'An error occurred while setting system mode'},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ===============================
# NEW ENDPOINTS - ADDITIONAL FEATURES
# ===============================

@extend_schema(
    responses={200: SystemStatusSerializer},
    description="Get combined system status - latest moisture, motors, mode, and thresholds in one call"
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def get_system_status(request):
    """
    Combined endpoint returning latest moisture, all motor states, system mode, and thresholds.
    Single call for mobile app dashboard.
    """
    try:
        # Get latest moisture reading
        latest_moisture = SoilMoisture.objects.order_by('-created_at').first()
        
        # Get all motors
        motors = Motor.objects.all()
        
        # Get system mode
        system_mode = SystemMode.get_instance()
        
        # Get all threshold configs
        thresholds = ThresholdConfig.objects.all()
        
        response_data = {
            'latest_moisture': SoilMoistureSerializer(latest_moisture).data if latest_moisture else None,
            'motors': MotorSerializer(motors, many=True).data,
            'system_mode': SystemModeSerializer(system_mode).data,
            'thresholds': ThresholdConfigSerializer(thresholds, many=True).data,
            'timestamp': timezone.now()
        }
        
        return create_response(
            success=True,
            data=response_data,
            message='System status retrieved successfully'
        )
    
    except Exception as e:
        logger.error(f"Error retrieving system status: {str(e)}", exc_info=True)
        return create_response(
            success=False,
            errors={'detail': 'An error occurred while retrieving system status'},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    parameters=[
        OpenApiParameter(name='nodeid', type=str, description='Filter by node ID'),
        OpenApiParameter(name='start_date', type=OpenApiTypes.DATETIME, description='Start date (YYYY-MM-DD or ISO format)'),
        OpenApiParameter(name='end_date', type=OpenApiTypes.DATETIME, description='End date (YYYY-MM-DD or ISO format)'),
        OpenApiParameter(name='page', type=int, description='Page number'),
        OpenApiParameter(name='page_size', type=int, description='Items per page (max: 1000)'),
    ],
    responses={200: SoilMoistureSerializer(many=True)},
    description="List soil moisture data with date range and node filtering"
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def list_soil_moisture_filtered(request):
    """
    Enhanced list endpoint with date range and node filtering.
    Query params: nodeid, start_date, end_date, page, page_size
    """
    try:
        from datetime import datetime
        
        queryset = SoilMoisture.objects.all()
        
        # Filter by nodeid
        nodeid = request.query_params.get('nodeid')
        if nodeid:
            queryset = queryset.filter(nodeid=nodeid)
        
        # Filter by date range
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            try:
                start = timezone.make_aware(datetime.fromisoformat(start_date.replace('Z', '+00:00')))
                queryset = queryset.filter(timestamp__gte=start)
            except ValueError:
                return create_response(
                    success=False,
                    errors={'start_date': 'Invalid date format. Use YYYY-MM-DD or ISO format'},
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        
        if end_date:
            try:
                end = timezone.make_aware(datetime.fromisoformat(end_date.replace('Z', '+00:00')))
                queryset = queryset.filter(timestamp__lte=end)
            except ValueError:
                return create_response(
                    success=False,
                    errors={'end_date': 'Invalid date format. Use YYYY-MM-DD or ISO format'},
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 100))
        
        if page < 1 or page_size < 1 or page_size > 1000:
            return create_response(
                success=False,
                errors={'pagination': 'Invalid pagination parameters'},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        total_count = queryset.count()
        offset = (page - 1) * page_size
        records = queryset[offset:offset + page_size]
        
        serializer = SoilMoistureSerializer(records, many=True)
        
        return create_response(
            success=True,
            data={
                'records': serializer.data,
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total_count': total_count,
                    'total_pages': (total_count + page_size - 1) // page_size if total_count > 0 else 0
                },
                'filters': {
                    'nodeid': nodeid,
                    'start_date': start_date,
                    'end_date': end_date
                }
            },
            message='Filtered records retrieved successfully'
        )
    
    except Exception as e:
        logger.error(f"Error retrieving filtered data: {str(e)}", exc_info=True)
        return create_response(
            success=False,
            errors={'detail': 'An error occurred while retrieving filtered data'},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    responses={200: ThresholdConfigSerializer},
    description="Get all moisture threshold configurations (per nodeid)"
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def get_thresholds(request):
    """Get all threshold configurations."""
    try:
        # Get nodeid from query params if provided
        nodeid = request.query_params.get('nodeid')
        
        if nodeid:
            # Get specific threshold config for nodeid
            config = ThresholdConfig.get_instance(nodeid)
            serializer = ThresholdConfigSerializer(config)
            return create_response(
                success=True,
                data={'threshold': serializer.data},
                message=f'Threshold config for {nodeid} retrieved successfully'
            )
        else:
            # Get all threshold configs
            configs = ThresholdConfig.objects.all()
            serializer = ThresholdConfigSerializer(configs, many=True)
            return create_response(
                success=True,
                data={'thresholds': serializer.data},
                message='All threshold configs retrieved successfully'
            )
    except Exception as e:
        logger.error(f"Error retrieving thresholds: {str(e)}", exc_info=True)
        return create_response(
            success=False,
            errors={'detail': 'An error occurred while retrieving thresholds'},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    request=ThresholdConfigSerializer,
    responses={200: ThresholdConfigSerializer},
    description="Update or create moisture threshold configuration for a nodeid"
)
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def set_thresholds(request):
    """
    Update or create threshold configuration for a specific nodeid.
    POST with {"nodeid": "sensor_zone1", "low_threshold": 30.0, "high_threshold": 70.0}
    """
    try:
        nodeid = request.data.get('nodeid')
        if not nodeid:
            return create_response(
                success=False,
                errors={'nodeid': 'nodeid is required'},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create sensor for this nodeid
        sensor, _ = Sensor.objects.get_or_create(nodeid=nodeid)
        
        # Get or create config for this sensor
        config = ThresholdConfig.get_or_create_for_sensor(sensor)
        serializer = ThresholdConfigSerializer(config, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Thresholds updated for {nodeid}: threshold={serializer.data['threshold']}")
            return create_response(
                success=True,
                data={'threshold': serializer.data},
                message=f'Thresholds for {nodeid} updated successfully'
            )
        
        return create_response(
            success=False,
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    except Exception as e:
        logger.error(f"Error setting thresholds: {str(e)}", exc_info=True)
        return create_response(
            success=False,
            errors={'detail': str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    responses={200: HealthCheckSerializer},
    description="System health check - database status and last sensor update"
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def health_check(request):
    """System health check endpoint."""
    try:
        from django.db import connection
        
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        db_status = "healthy"
        
        # Get last sensor update
        latest_reading = SoilMoisture.objects.order_by('-created_at').first()
        last_update = latest_reading.created_at if latest_reading else None
        
        time_since_update = None
        if last_update:
            delta = timezone.now() - last_update
            if delta.total_seconds() < 60:
                time_since_update = f"{int(delta.total_seconds())} seconds ago"
            elif delta.total_seconds() < 3600:
                time_since_update = f"{int(delta.total_seconds() / 60)} minutes ago"
            else:
                time_since_update = f"{int(delta.total_seconds() / 3600)} hours ago"
        
        # Count motors
        motors_count = Motor.objects.count()
        
        health_data = {
            'status': 'healthy',
            'database': db_status,
            'last_sensor_update': last_update,
            'time_since_last_update': time_since_update,
            'motors_count': motors_count,
            'timestamp': timezone.now()
        }
        
        return create_response(
            success=True,
            data=health_data,
            message='System is healthy'
        )
    
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        return create_response(
            success=False,
            data={
                'status': 'unhealthy',
                'database': 'error',
                'error': str(e),
                'timestamp': timezone.now()
            },
            message='System health check failed',
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )


@extend_schema(
    responses={200: DashboardStatsSerializer},
    description="Dashboard statistics - readings count, averages, motor status"
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def dashboard_stats(request):
    """Get statistics for dashboard display."""
    try:
        from datetime import timedelta
        from django.db.models import Avg
        
        # Total readings
        total_readings = SoilMoisture.objects.count()
        
        # Average moisture last 24 hours
        yesterday = timezone.now() - timedelta(hours=24)
        avg_24h = SoilMoisture.objects.filter(
            timestamp__gte=yesterday
        ).aggregate(avg=Avg('value'))['avg'] or 0.0
        
        # Average moisture last 7 days
        week_ago = timezone.now() - timedelta(days=7)
        avg_7d = SoilMoisture.objects.filter(
            timestamp__gte=week_ago
        ).aggregate(avg=Avg('value'))['avg'] or 0.0
        
        # Motor counts
        motors_on = Motor.objects.filter(state='ON').count()
        motors_off = Motor.objects.filter(state='OFF').count()
        
        # System mode
        system_mode = SystemMode.get_current_mode()
        
        # Last reading time
        latest = SoilMoisture.objects.order_by('-created_at').first()
        last_reading_time = latest.created_at if latest else None
        
        # Unique nodes
        unique_nodes = SoilMoisture.objects.values('nodeid').distinct().count()
        
        stats = {
            'total_readings': total_readings,
            'avg_moisture_24h': round(avg_24h, 2),
            'avg_moisture_7d': round(avg_7d, 2),
            'motors_on_count': motors_on,
            'motors_off_count': motors_off,
            'system_mode': system_mode,
            'last_reading_time': last_reading_time,
            'unique_nodes': unique_nodes
        }
        
        return create_response(
            success=True,
            data=stats,
            message='Dashboard statistics retrieved successfully'
        )
    
    except Exception as e:
        logger.error(f"Error retrieving dashboard stats: {str(e)}", exc_info=True)
        return create_response(
            success=False,
            errors={'detail': 'An error occurred while retrieving statistics'},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    request=BulkMotorControlSerializer,
    responses={200: MotorSerializer(many=True)},
    description="Control multiple motors at once in MANUAL mode"
)
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def bulk_motor_control(request):
    """
    Bulk motor control endpoint.
    POST with {"motors": [{"id": 1, "state": "ON"}, {"id": 2, "state": "OFF"}]}
    Only works in MANUAL mode.
    """
    try:
        # Check system mode
        current_mode = SystemMode.get_current_mode()
        
        if current_mode != 'MANUAL':
            return create_response(
                success=False,
                errors={'detail': 'Bulk motor control only available in MANUAL mode'},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate request data
        serializer = BulkMotorControlSerializer(data=request.data)
        if not serializer.is_valid():
            return create_response(
                success=False,
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        motors_data = serializer.validated_data['motors']
        updated_motors = []
        errors = []
        
        # Update each motor
        for motor_data in motors_data:
            motor_id = motor_data['id']
            state = motor_data['state']
            
            try:
                motor = Motor.objects.get(id=motor_id)
                motor.state = state
                motor.save()
                updated_motors.append(motor)
                logger.info(f"Motor {motor_id} set to {state} (bulk control)")
            except Motor.DoesNotExist:
                errors.append({'id': motor_id, 'error': 'Motor not found'})
        
        response_data = {
            'updated_motors': MotorSerializer(updated_motors, many=True).data,
            'updated_count': len(updated_motors)
        }
        
        if errors:
            response_data['errors'] = errors
        
        return create_response(
            success=True,
            data=response_data,
            message=f'{len(updated_motors)} motor(s) updated successfully'
        )
    
    except Exception as e:
        logger.error(f"Error in bulk motor control: {str(e)}", exc_info=True)
        return create_response(
            success=False,
            errors={'detail': 'An error occurred during bulk motor control'},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ===============================
# SIMPLE MOTOR INFO ENDPOINT
# ===============================

@extend_schema(
    responses={200: OpenApiResponse(
        description="Simple motor status by name",
        examples=[
            OpenApiExample(
                'Motors Info Response',
                value={
                    "motor1": "ON",
                    "motor2": "OFF",
                    "pump_a": "ON"
                }
            )
        ]
    )},
    description="Get simple motor status - returns motor states by name without IDs or extra metadata"
)
@api_view(['GET'])
@csrf_exempt
@authentication_classes([])
@permission_classes([AllowAny])
def motors_info(request):
    """
    Simple endpoint that returns motor states by sensor nodeid.
    Returns: {"sensor_zone1": "ON", "sensor_zone2": "OFF", ...}
    No authentication required, CSRF exempt for IoT devices.
    """
    try:
        motors = Motor.objects.select_related('sensor').all()
        
        # Build simple dict with sensor nodeid as key and state as value
        motors_dict = {motor.sensor.nodeid: motor.state for motor in motors}
        
        logger.info(f"Motors info requested from IP: {request.META.get('REMOTE_ADDR')}")
        
        return Response(motors_dict, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error retrieving motors info: {str(e)}", exc_info=True)
        return Response(
            {"error": "An error occurred while retrieving motors info"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
