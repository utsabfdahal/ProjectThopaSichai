# 🎯 Quick Reference: Better Code Patterns

## Model Usage Examples

### ✅ Motor Model

```python
# Old way ❌
motor = Motor.objects.get(id=1)
motor.state = 'ON'
motor.save()

if motor.state == 'ON':
    print("Running")

# New way ✅
motor = Motor.objects.get(id=1)
motor.turn_on()  # Built-in method

if motor.is_on:  # Property, not method
    print("Running")

# Other methods
motor.turn_off()
motor.toggle()
```

### ✅ SystemMode Model

```python
# Old way ❌
mode = SystemMode.get_current_mode()
if mode == 'MANUAL':
    # do something

# New way ✅
if SystemMode.is_manual():
    # do something

if SystemMode.is_automatic():
    # do something

# Set mode
SystemMode.set_mode(SystemMode.Mode.MANUAL)
# Or
SystemMode.set_mode('MANUAL')  # Still works
```

### ✅ SoilMoisture Model

```python
# Get latest reading for a node
reading = SoilMoisture.get_latest_by_node('ESP32_001')

# Get average value
avg = SoilMoisture.get_average_value(nodeid='ESP32_001', hours=24)

# Properties
print(reading.moisture_status)  # 'DRY', 'OPTIMAL', 'WET', or 'SATURATED'
print(reading.age_seconds)  # Seconds since created
```

---

## Serializer Usage Examples

### ✅ Using New Convenience Serializers

```python
# In views - Motor Control
@api_view(['POST'])
def control_motor(request, motor_id):
    # Old way ❌
    state = request.data.get('state', '').upper()
    if state not in ['ON', 'OFF']:
        return Response({'error': 'Invalid state'}, status=400)
    
    # New way ✅
    serializer = MotorControlSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    
    state = serializer.validated_data['state']
    motor = Motor.objects.get(id=motor_id)
    
    if state == 'ON':
        motor.turn_on()
    else:
        motor.turn_off()
    
    return Response(MotorSerializer(motor).data)
```

### ✅ Using Enhanced Output Fields

```python
# Motor serializer now includes:
{
    "id": 1,
    "name": "Pump 1",
    "state": "ON",
    "state_display": "On",  # ✨ Human readable
    "is_on": true,          # ✨ Boolean helper
    "created_at": "...",
    "updated_at": "..."
}

# SoilMoisture serializer now includes:
{
    "id": "uuid",
    "nodeid": "ESP32_001",
    "value": 45.5,
    "moisture_status": "OPTIMAL",  # ✨ Status category
    "age_seconds": 120,            # ✨ How old
    "timestamp": "...",
    "created_at": "...",
    "updated_at": "..."
}
```

---

## View Improvements

### ✅ Using Model Methods in Views

```python
# Before ❌
@api_view(['POST'])
def receive_soil_moisture(request):
    # ... save data ...
    
    if SystemMode.get_current_mode() == 'AUTOMATIC':
        motors = Motor.objects.all()
        for motor in motors:
            if should_turn_on:
                motor.state = 'ON'
                motor.save()

# After ✅
@api_view(['POST'])
def receive_soil_moisture(request):
    # ... save data ...
    
    if SystemMode.is_automatic():
        motors = Motor.objects.all()
        for motor in motors:
            if should_turn_on:
                motor.turn_on()  # Optimized save
            else:
                motor.turn_off()
```

---

## Validation Examples

### ✅ Automatic Validation

```python
# Models now have built-in validators
class SoilMoisture(models.Model):
    value = models.FloatField(
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(100.0)
        ]
    )

# This will automatically raise ValidationError:
reading = SoilMoisture(nodeid='ESP32', value=150)  # ❌ > 100
reading.full_clean()  # Raises ValidationError
```

### ✅ Serializer Validation

```python
# Serializers now use extra_kwargs
class Meta:
    extra_kwargs = {
        'name': {
            'min_length': 1,
            'trim_whitespace': True,
            'error_messages': {
                'blank': 'Motor name cannot be empty'
            }
        }
    }

# No need for custom validate_name method!
```

---

## TextChoices Usage

### ✅ Type-Safe Choices

```python
# Access choices safely
Motor.State.ON      # 'ON'
Motor.State.OFF     # 'OFF'
Motor.State.choices # List of tuples

# Use in code
motor.state = Motor.State.ON  # ✅ Type-safe
motor.state = 'ON'            # ✅ Still works

# Compare safely
if motor.state == Motor.State.ON:  # ✅ No typos!
    print("Running")

# Get display value
motor.get_state_display()  # 'On'
```

---

## Query Optimization

### ✅ Using update_fields

```python
# Old way ❌
motor.state = 'ON'
motor.save()  # Updates ALL fields in database

# New way ✅
motor.turn_on()  # Only updates state and updated_at
# Internally: save(update_fields=['state', 'updated_at'])
```

### ✅ Using Indexes

```python
# Queries are now faster due to indexes:
Motor.objects.filter(state='ON')  # ✅ Uses index
SoilMoisture.objects.filter(nodeid='ESP32_001')  # ✅ Uses index
SoilMoisture.objects.order_by('-timestamp')  # ✅ Uses index
```

---

## Mixin Usage

### ✅ Creating Your Own Mixins

```python
# Example: Add description field to multiple models
class DescriptionMixin(models.Model):
    description = models.TextField(blank=True)
    
    class Meta:
        abstract = True

class Motor(DescriptionMixin, TimeStampedModel):
    # Now has: description, created_at, updated_at
    pass
```

---

## Error Messages

### ✅ Custom Error Messages

```python
# In serializers
class Meta:
    extra_kwargs = {
        'value': {
            'error_messages': {
                'invalid': 'Must be a number',
                'required': 'Moisture value is required'
            }
        }
    }

# In models
value = models.FloatField(
    validators=[
        MinValueValidator(0.0, message="Cannot be negative")
    ]
)
```

---

## Testing Examples

### ✅ Testing Model Methods

```python
def test_motor_turn_on():
    motor = Motor.objects.create(name='Test', state=Motor.State.OFF)
    assert not motor.is_on
    
    motor.turn_on()
    assert motor.is_on
    assert motor.state == Motor.State.ON

def test_system_mode_singleton():
    mode1 = SystemMode.get_instance()
    mode2 = SystemMode.get_instance()
    assert mode1.id == mode2.id == 1
```

---

## Common Patterns

### ✅ Pattern: Conditional Motor Control

```python
def update_motor_based_on_moisture(moisture_value):
    """Update motor based on sensor reading."""
    motor = Motor.objects.get(name='Main Pump')
    
    if moisture_value < 30:
        motor.turn_on()
    elif moisture_value > 70:
        motor.turn_off()
    # Hysteresis: don't change between 30-70
```

### ✅ Pattern: Get or Set Mode

```python
def ensure_manual_mode():
    """Ensure system is in manual mode."""
    if not SystemMode.is_manual():
        SystemMode.set_mode(SystemMode.Mode.MANUAL)
```

### ✅ Pattern: Latest Reading with Fallback

```python
def get_moisture_or_default(nodeid, default=50.0):
    """Get latest moisture or default value."""
    reading = SoilMoisture.get_latest_by_node(nodeid)
    return reading.value if reading else default
```

---

## Migration from Old Code

### ✅ Step-by-Step Migration

**1. Update model references:**
```python
# Before
if mode.mode == 'MANUAL':

# After
if SystemMode.is_manual():
```

**2. Update state changes:**
```python
# Before
motor.state = 'ON'
motor.save()

# After
motor.turn_on()
```

**3. Update serializer usage:**
```python
# Before
def validate_state(self, value):
    if value not in ['ON', 'OFF']:
        raise ValidationError("Invalid")
    return value

# After
# Use MotorControlSerializer or extra_kwargs
```

---

## 💡 Pro Tips

### Tip 1: Use Properties for Computed Values
```python
@property
def is_outdated(self):
    """Check if reading is older than 5 minutes."""
    return self.age_seconds > 300
```

### Tip 2: Use Class Methods for Queries
```python
@classmethod
def get_active_motors(cls):
    """Get all motors that are ON."""
    return cls.objects.filter(state=cls.State.ON)
```

### Tip 3: Use Serializer Context
```python
serializer = SoilMoistureSerializer(
    reading,
    context={'motor_recommendation': motor_data}
)
```

### Tip 4: Chain Query Methods
```python
recent_dry = SoilMoisture.objects.filter(
    timestamp__gte=timezone.now() - timedelta(hours=1)
).filter(
    value__lt=30
).order_by('-timestamp')
```

---

## 🎯 Key Takeaways

1. **Use model methods** for business logic, not views
2. **Use properties** for computed values
3. **Use TextChoices** for type safety
4. **Use validators** in models, not serializers
5. **Use extra_kwargs** for serializer configuration
6. **Use mixins** for reusable functionality
7. **Use class methods** for common queries
8. **Use update_fields** for performance

---

## ✅ Quick Checklist

When writing new code, ask yourself:

- [ ] Is this business logic? → Put in model
- [ ] Is this validation? → Use validators or extra_kwargs
- [ ] Is this a computed value? → Use @property
- [ ] Is this a common query? → Use @classmethod
- [ ] Am I repeating code? → Create a mixin
- [ ] Am I using magic strings? → Use TextChoices
- [ ] Am I updating one field? → Use update_fields
- [ ] Are my errors descriptive? → Use error_messages

---

**Happy Coding!** 🚀
