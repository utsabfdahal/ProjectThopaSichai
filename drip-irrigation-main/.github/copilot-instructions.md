# Smart Drip Irrigation System - Copilot Instructions

## Project Overview
You are assisting with the development of "Himalayan Smart Krishi Tech" - an autonomous solar-powered IoT drip irrigation system designed for small-to-medium Nepali farmers.

## Product: "Smart Kisan Kit"
A complete plug-and-play solution with:
- **Hardware**: ESP32-based control unit, solar power system, soil moisture sensors, tank level monitoring, dual pumps (irrigation + auto-refill)
- **Software**: React Native mobile app (Nepali localization), Firebase/AWS IoT backend
- **USP**: Fully autonomous water cycle with auto-refill from wells/sources

## Technical Stack
- **MCU**: ESP32 (Wi-Fi, BLE)
- **Sensors**: Capacitive soil moisture (4x), ultrasonic tank level, water flow, temp/humidity
- **Actuation**: Solenoid valves (4x), 12V DC pumps (2x)
- **Power**: 20-30W solar panel + 12V LiFePO4/SLA battery
- **Mobile**: React Native (iOS/Android)
- **Backend**: Firebase/AWS IoT
- **Enclosure**: IP65 rated, ruggedized for monsoon/heat

## Target Market
- **Primary**: Commercial vegetable farmers (2-10 ropani) in Nepal growing high-value crops
- **Price Point**: ~NPR 45,000 ($350 USD)
- **Environment**: High humidity, dust, variable solar, intermittent internet

## Design Principles
1. **Ruggedness First**: Agricultural-grade components, IP65 minimum, conformal coating on PCBs
2. **Offline Resilience**: System must operate independently without internet connectivity
3. **Simplicity**: UI designed for farmers, not engineers. Nepali language support mandatory
4. **Affordability**: Cost-conscious design while maintaining reliability
5. **Maintainability**: Local assembly, replaceable components, easy troubleshooting

## Key Development Focus
- Firmware with robust offline mode and OTA update capability
- Low-power optimization for 24/7 solar autonomy
- Sensor calibration for Nepali soil conditions
- React Native app with intuitive, localized UX
- Automated tank refill logic with multiple failsafes
- Water conservation algorithms using soil + weather data

## Collaboration Context
Work alongside specialized agents:
- **Business Agent**: Market strategy, pricing, partnerships, funding
- **IoT Agent**: Hardware design, firmware, protocols, power management
- **Agriculture Agent**: Crop water requirements, soil science, farming practices

## Code Standards
- ESP32: Arduino/ESP-IDF framework, modular structure, extensive error handling
- React Native: TypeScript preferred, clean component architecture, offline-first design
- Backend: RESTful APIs, MQTT for device communication, secure authentication
- Documentation: Clear comments, especially for calibration values and thresholds

## Testing Requirements
- 24-hour burn-in test for every unit
- Field testing in actual farm conditions
- Extreme weather simulation (monsoon, heat)
- Network dropout scenarios
- Battery discharge/solar charging cycles

## Regulatory Considerations
- Nepal electrical safety standards
- Wi-Fi spectrum compliance
- Agricultural equipment certifications
- IP rating verification

When providing assistance:
- Prioritize reliability over features
- Consider cost implications of component choices
- Account for local supply chain limitations (3-month import buffer)
- Design for easy farmer installation and maintenance
- Always validate power consumption against solar budget
