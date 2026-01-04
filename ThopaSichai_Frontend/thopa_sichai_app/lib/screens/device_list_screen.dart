import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'motors_screen.dart';

class DeviceListScreen extends StatefulWidget {
  const DeviceListScreen({super.key});

  @override
  State<DeviceListScreen> createState() => _DeviceListScreenState();
}

class _DeviceListScreenState extends State<DeviceListScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  
  // Sensors data
  List<Map<String, dynamic>> _sensors = [];
  List<dynamic> _motors = [];
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _fetchDevices();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _fetchDevices() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      // Fetch sensor data
      final readings = await ApiService.getSoilMoistureData(pageSize: 100);
      
      // Group by nodeid to get unique sensors
      final Map<String, Map<String, dynamic>> sensorMap = {};
      for (var record in readings) {
        final nodeid = record['nodeid']?.toString() ?? 'unknown';
        if (!sensorMap.containsKey(nodeid)) {
          sensorMap[nodeid] = {
            'nodeid': nodeid,
            'lastValue': record['value'],
            'lastUpdate': record['timestamp'],
            'ipAddress': record['ip_address'] ?? 'N/A',
            'status': record['moisture_status'] ?? '',
          };
        }
      }

      // Fetch motors
      List<dynamic> motors = [];
      try {
        motors = await ApiService.getMotors();
      } catch (_) {}

      if (mounted) {
        setState(() {
          _sensors = sensorMap.values.toList();
          _motors = motors;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = e.toString().replaceAll('Exception: ', '');
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1A1C1E),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1A1C1E),
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Devices',
          style: TextStyle(
            color: Colors.white,
            fontSize: 20,
            fontWeight: FontWeight.w600,
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Color(0xFF7DC2FF)),
            onPressed: _fetchDevices,
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.green,
          labelColor: Colors.green,
          unselectedLabelColor: Colors.white54,
          tabs: [
            Tab(text: 'Sensors (${_sensors.length})'),
            Tab(text: 'Motors (${_motors.length})'),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Colors.green))
          : _errorMessage != null
              ? _buildErrorView()
              : TabBarView(
                  controller: _tabController,
                  children: [
                    _buildSensorsList(),
                    _buildMotorsList(),
                  ],
                ),
    );
  }

  Widget _buildErrorView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline, color: Colors.red, size: 64),
          const SizedBox(height: 16),
          Text(_errorMessage!, style: const TextStyle(color: Colors.white)),
          const SizedBox(height: 16),
          ElevatedButton(onPressed: _fetchDevices, child: const Text('Retry')),
        ],
      ),
    );
  }

  Widget _buildSensorsList() {
    if (_sensors.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.sensors_off, color: Colors.white38, size: 64),
            SizedBox(height: 16),
            Text('No sensors found', style: TextStyle(color: Colors.white54)),
          ],
        ),
      );
    }
    return RefreshIndicator(
      onRefresh: _fetchDevices,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _sensors.length,
        itemBuilder: (context, index) => _buildSensorCard(_sensors[index]),
      ),
    );
  }

  Widget _buildMotorsList() {
    if (_motors.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.settings_applications, color: Colors.white38, size: 64),
            const SizedBox(height: 16),
            const Text('No motors configured', style: TextStyle(color: Colors.white54)),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const MotorsScreen()),
              ),
              icon: const Icon(Icons.add),
              label: const Text('Add Motor'),
            ),
          ],
        ),
      );
    }
    return RefreshIndicator(
      onRefresh: _fetchDevices,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _motors.length + 1,
        itemBuilder: (context, index) {
          if (index == _motors.length) {
            return Padding(
              padding: const EdgeInsets.symmetric(vertical: 16),
              child: Center(
                child: TextButton.icon(
                  onPressed: () => Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => const MotorsScreen()),
                  ),
                  icon: const Icon(Icons.settings, color: Colors.blue),
                  label: const Text('Manage Motors', style: TextStyle(color: Colors.blue)),
                ),
              ),
            );
          }
          return _buildMotorCard(_motors[index]);
        },
      ),
    );
  }

  Widget _buildSensorCard(Map<String, dynamic> sensor) {
    final nodeid = sensor['nodeid'] ?? 'Unknown';
    final lastValue = double.tryParse(sensor['lastValue']?.toString() ?? '0') ?? 0;
    final ipAddress = sensor['ipAddress'] ?? 'N/A';
    final status = sensor['status'] ?? '';
    
    Color statusColor = Colors.green;
    if (lastValue < 30) statusColor = Colors.red;
    else if (lastValue > 70) statusColor = Colors.blue;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: const Color(0xFF212529),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: statusColor.withOpacity(0.2),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(Icons.sensors, color: statusColor, size: 28),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    nodeid,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'IP: $ipAddress',
                    style: TextStyle(color: Colors.white.withOpacity(0.5), fontSize: 12),
                  ),
                ],
              ),
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  '${lastValue.toInt()}%',
                  style: TextStyle(
                    color: statusColor,
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                if (status.isNotEmpty)
                  Text(status, style: TextStyle(color: statusColor, fontSize: 12)),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMotorCard(Map<String, dynamic> motor) {
    final id = motor['id'];
    final name = motor['name'] ?? 'Motor $id';
    final isOn = motor['state'] == 'ON';
    final pin = motor['pin'] ?? 'N/A';

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: const Color(0xFF212529),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isOn ? Colors.green.withOpacity(0.5) : Colors.transparent,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: (isOn ? Colors.green : Colors.grey).withOpacity(0.2),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                Icons.settings_applications,
                color: isOn ? Colors.green : Colors.grey,
                size: 28,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    name,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Pin: $pin',
                    style: TextStyle(color: Colors.white.withOpacity(0.5), fontSize: 12),
                  ),
                ],
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                color: (isOn ? Colors.green : Colors.grey).withOpacity(0.2),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Text(
                isOn ? 'ON' : 'OFF',
                style: TextStyle(
                  color: isOn ? Colors.green : Colors.grey,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
