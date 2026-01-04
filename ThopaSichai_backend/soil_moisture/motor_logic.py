"""
Motor control logic for soil moisture system.
This module contains the business logic for determining motor state based on sensor readings.
"""
import logging
from typing import Dict, Literal

logger = logging.getLogger('soil_moisture')

# Default threshold - motor turns ON when moisture exceeds this value
DEFAULT_THRESHOLD = 50.0


class MotorController:
    """
    Controller class to determine motor state based on soil moisture readings.
    Motor turns ON when moisture value exceeds threshold.
    """
    
    def __init__(self, threshold: float = DEFAULT_THRESHOLD):
        """
        Initialize motor controller with threshold.
        
        Args:
            threshold: Motor turns ON when moisture value exceeds this
        """
        if not 0 <= threshold <= 100:
            raise ValueError("threshold must be between 0 and 100")
        
        self.threshold = threshold
        logger.info(f"MotorController initialized with threshold: {threshold}%")
    
    def determine_motor_state(self, current_moisture: float, 
                             current_motor_state: Literal['ON', 'OFF'] = 'OFF') -> Dict:
        """
        Determine if motor should be ON or OFF based on current moisture level.
        Motor turns ON when moisture > threshold, OFF otherwise.
        
        Args:
            current_moisture: Current soil moisture percentage
            current_motor_state: Current state of the motor (ignored in this logic)
        
        Returns:
            Dict with motor state decision and reason:
            {
                'desired_state': 'ON' or 'OFF',
                'reason': explanation string,
                'moisture_level': current moisture value,
                'threshold': threshold value
            }
        """
        logger.debug(f"Determining motor state: moisture={current_moisture}%, threshold={self.threshold}%")
        
        # Validate input
        if not isinstance(current_moisture, (int, float)):
            raise ValueError("current_moisture must be a number")
        
        # Simple logic: motor ON if moisture > threshold
        if current_moisture > self.threshold:
            desired_state = 'ON'
            reason = f"Moisture level {current_moisture}% exceeds threshold {self.threshold}%"
        else:
            desired_state = 'OFF'
            reason = f"Moisture level {current_moisture}% is below or equal to threshold {self.threshold}%"
        
        result = {
            'desired_state': desired_state,
            'reason': reason,
            'moisture_level': current_moisture,
            'threshold': self.threshold
        }
        
        logger.info(f"Motor decision: {desired_state} - {reason}")
        return result


def get_motor_state(moisture_value: float, 
                   current_state: Literal['ON', 'OFF'] = 'OFF',
                   threshold: float = DEFAULT_THRESHOLD) -> Dict:
    """
    Convenience function to determine motor state without creating a controller instance.
    
    Args:
        moisture_value: Current soil moisture percentage
        current_state: Current motor state (ignored in single threshold logic)
        threshold: Motor turns ON when moisture value exceeds this
    
    Returns:
        Dict with motor state decision and reason
    """
    controller = MotorController(threshold)
    return controller.determine_motor_state(moisture_value, current_state)

