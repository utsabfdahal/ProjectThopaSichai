import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'device_list_screen.dart';
import 'soil_moisture_screen.dart';
import 'history_screen.dart';
import 'settings_screen.dart';
import 'add_device_screen.dart';
import 'motors_screen.dart';
import '../services/api_service.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  // Data state
  List<dynamic> _recentReadings = [];
  List<dynamic> _motors = [];
  List<String> _sensorNodes = [];
  String _systemMode = 'MANUAL';
  bool _isLoading = true;
  String? _errorMessage;
  bool _ultrasonicAlertShown = false; // Track if alert has been shown

  // Stats
  double _latestMoisture = 0.0;
  double _avgMoisture = 0.0;
  int _totalReadings = 0;
  int _motorsOn = 0;
  int _motorsOff = 0;

  @override
  void initState() {
    super.initState();
    _loadDashboardData();
  }

  void _showUltrasonicAlert() {
    if (_ultrasonicAlertShown) return; // Don't show again if already shown
    _ultrasonicAlertShown = true;
    
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF212529),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Row(
          children: [
            Icon(Icons.warning_amber_rounded, color: Colors.orange, size: 28),
            SizedBox(width: 8),
            Text(
              'Sensor Alert',
              style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
            ),
          ],
        ),
        content: const Text(
          'Ultrasonic sensor value has exceeded the threshold.\nPlease turn off the ultrasonic motor.',
          style: TextStyle(color: Colors.white70),
        ),
        actions: [
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF4CAF50),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
            child: const Text('OK', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  Future<void> _checkUltrasonicThreshold(List<dynamic> readings) async {
    try {
      // Get thresholds
      final thresholdsResponse = await ApiService.getThresholds();
      if (thresholdsResponse['success'] != true || thresholdsResponse['data'] == null) return;
      
      final thresholds = thresholdsResponse['data']['thresholds'] as List<dynamic>? ?? [];
      
      // Find us00 threshold
      double? us00Threshold;
      for (var t in thresholds) {
        if (t['nodeid'] == 'us00' || t['nodeid'] == 'us01') {
          us00Threshold = (t['threshold'] as num?)?.toDouble();
          break;
        }
      }
      
      if (us00Threshold == null) return;
      
      // Find latest us00 reading
      for (var reading in readings) {
        final nodeId = reading['nodeid']?.toString() ?? '';
        if (nodeId == 'us00' || nodeId == 'us01') {
          final value = double.tryParse(reading['value'].toString()) ?? 0;
          if (value >= us00Threshold && mounted) {
            _showUltrasonicAlert();
          }
          break;
        }
      }
    } catch (_) {}
  }

  Future<void> _loadDashboardData() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      // Fetch soil moisture data
      final readings = await ApiService.getSoilMoistureData(pageSize: 50);
      
      // Calculate stats from readings
      double sum = 0;
      int count = 0;
      final nodeIds = <String>{};
      
      for (var reading in readings) {
        try {
          sum += double.parse(reading['value'].toString());
          count++;
          if (reading['nodeid'] != null) {
            nodeIds.add(reading['nodeid'].toString());
          }
        } catch (_) {}
      }

      final latest = readings.isNotEmpty 
          ? double.tryParse(readings.first['value'].toString()) ?? 0.0 
          : 0.0;
      final avg = count > 0 ? sum / count : 0.0;

      // Try to fetch motors (may fail if no motors configured)
      List<dynamic> motors = [];
      try {
        motors = await ApiService.getMotors();
      } catch (_) {}

      // Try to fetch system mode
      String mode = 'MANUAL';
      try {
        final modeData = await ApiService.getSystemMode();
        mode = modeData['mode'] ?? 'MANUAL';
      } catch (_) {}

      // Count motors on/off
      int on = 0, off = 0;
      for (var motor in motors) {
        if (motor['state'] == 'ON') {
          on++;
        } else {
          off++;
        }
      }

      if (mounted) {
        setState(() {
          _recentReadings = readings;
          _motors = motors;
          _sensorNodes = nodeIds.toList();
          _systemMode = mode;
          _latestMoisture = latest;
          _avgMoisture = avg;
          _totalReadings = readings.length;
          _motorsOn = on;
          _motorsOff = off;
          _isLoading = false;
        });
        
        // Check ultrasonic sensor threshold
        _checkUltrasonicThreshold(readings);
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
          _errorMessage = e.toString().replaceAll('Exception: ', '');
        });
      }
    }
  }

  Future<void> _toggleMotor(int motorId, bool turnOn) async {
    try {
      await ApiService.controlMotor(motorId, turnOn);
      _loadDashboardData(); // Refresh
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Motor ${turnOn ? "ON" : "OFF"}'),
            backgroundColor: turnOn ? Colors.green : Colors.orange,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
        );
      }
    }
  }

  Future<void> _toggleSystemMode() async {
    final newMode = _systemMode == 'MANUAL' ? 'AUTOMATIC' : 'MANUAL';
    try {
      await ApiService.setSystemMode(newMode);
      setState(() => _systemMode = newMode);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Mode set to $newMode')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
        );
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
        title: const Text('Thopa Sichai', style: TextStyle(color: Colors.white)),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.white),
            onPressed: _loadDashboardData,
          ),
          IconButton(
            icon: const Icon(Icons.settings, color: Colors.white),
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const SettingsScreen()),
            ),
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _errorMessage != null
              ? _buildErrorView()
              : RefreshIndicator(
                  onRefresh: _loadDashboardData,
                  child: SingleChildScrollView(
                    physics: const AlwaysScrollableScrollPhysics(),
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _buildStatsCards(),
                        const SizedBox(height: 20),
                        _buildMoistureChart(),
                        const SizedBox(height: 20),
                        _buildSensorNodesList(),
                        const SizedBox(height: 20),
                        _buildMotorsSection(),
                        const SizedBox(height: 20),
                        _buildRecentReadings(),
                        const SizedBox(height: 20),
                        _buildQuickActions(),
                        const SizedBox(height: 80),
                      ],
                    ),
                  ),
                ),
      floatingActionButton: FloatingActionButton(
        backgroundColor: const Color(0xFF4CAF50),
        onPressed: () => Navigator.push(
          context,
          MaterialPageRoute(builder: (_) => const AddDeviceScreen()),
        ),
        child: const Icon(Icons.add),
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
          ElevatedButton(
            onPressed: _loadDashboardData,
            child: const Text('Retry'),
          ),
        ],
      ),
    );
  }

  Widget _buildStatsCards() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Overview',
          style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(child: _buildStatCard('Latest', '${_latestMoisture.toStringAsFixed(1)}%', Icons.water_drop, Colors.blue)),
            const SizedBox(width: 12),
            Expanded(child: _buildStatCard('Average', '${_avgMoisture.toStringAsFixed(1)}%', Icons.analytics, Colors.green)),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(child: _buildStatCard('Sensors', '${_sensorNodes.length}', Icons.sensors, Colors.orange)),
            const SizedBox(width: 12),
            Expanded(child: _buildStatCard('Readings', '$_totalReadings', Icons.data_usage, Colors.purple)),
          ],
        ),
      ],
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF212529),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: color.withOpacity(0.2),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: color, size: 24),
          ),
          const SizedBox(width: 12),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title, style: TextStyle(color: Colors.white.withOpacity(0.7), fontSize: 12)),
              Text(value, style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMoistureChart() {
    if (_recentReadings.isEmpty) {
      return Container(
        height: 200,
        decoration: BoxDecoration(
          color: const Color(0xFF212529),
          borderRadius: BorderRadius.circular(12),
        ),
        child: const Center(
          child: Text('No data available', style: TextStyle(color: Colors.white54)),
        ),
      );
    }

    // Prepare chart data (last 20 readings, reversed for chronological order)
    final chartData = _recentReadings.take(20).toList().reversed.toList();
    final spots = <FlSpot>[];
    
    for (int i = 0; i < chartData.length; i++) {
      try {
        final value = double.parse(chartData[i]['value'].toString());
        spots.add(FlSpot(i.toDouble(), value));
      } catch (_) {}
    }

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF212529),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Moisture Trend',
                style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
              ),
              GestureDetector(
                onTap: () => Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const SoilMoistureScreen()),
                ),
                child: const Text('View All →', style: TextStyle(color: Color(0xFF4CAF50))),
              ),
            ],
          ),
          const SizedBox(height: 16),
          SizedBox(
            height: 200,
            child: LineChart(
              LineChartData(
                gridData: FlGridData(
                  show: true,
                  drawVerticalLine: false,
                  horizontalInterval: 25,
                  getDrawingHorizontalLine: (value) => FlLine(
                    color: Colors.white.withOpacity(0.1),
                    strokeWidth: 1,
                  ),
                ),
                titlesData: FlTitlesData(
                  leftTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      reservedSize: 40,
                      interval: 25,
                      getTitlesWidget: (value, meta) => Text(
                        '${value.toInt()}%',
                        style: TextStyle(color: Colors.white.withOpacity(0.5), fontSize: 10),
                      ),
                    ),
                  ),
                  bottomTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                ),
                borderData: FlBorderData(show: false),
                minY: 0,
                maxY: 100,
                lineBarsData: [
                  LineChartBarData(
                    spots: spots,
                    isCurved: true,
                    color: const Color(0xFF4CAF50),
                    barWidth: 3,
                    dotData: const FlDotData(show: false),
                    belowBarData: BarAreaData(
                      show: true,
                      color: const Color(0xFF4CAF50).withOpacity(0.2),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSensorNodesList() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF212529),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Active Sensors',
            style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          if (_sensorNodes.isEmpty)
            const Text('No sensors found', style: TextStyle(color: Colors.white54))
          else
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _sensorNodes.map((nodeId) => Chip(
                backgroundColor: const Color(0xFF4CAF50).withOpacity(0.2),
                label: Text(nodeId, style: const TextStyle(color: Color(0xFF4CAF50))),
                avatar: const Icon(Icons.sensors, color: Color(0xFF4CAF50), size: 18),
              )).toList(),
            ),
        ],
      ),
    );
  }

  Widget _buildMotorsSection() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF212529),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Motors',
                style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
              ),
              Row(
                children: [
                  Text(
                    _systemMode,
                    style: TextStyle(
                      color: _systemMode == 'AUTOMATIC' ? Colors.green : Colors.orange,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(width: 8),
                  GestureDetector(
                    onTap: _toggleSystemMode,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.blue.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: const Text('Toggle', style: TextStyle(color: Colors.blue, fontSize: 12)),
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 12),
          if (_motors.isEmpty)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 20),
              child: Center(
                child: Text('No motors configured', style: TextStyle(color: Colors.white54)),
              ),
            )
          else
            ..._motors.map((motor) => _buildMotorTile(motor)),
        ],
      ),
    );
  }

  Widget _buildMotorTile(Map<String, dynamic> motor) {
    final id = motor['id'] as int;
    final name = motor['name'] ?? 'Motor $id';
    final isOn = motor['state'] == 'ON';
    final isAuto = _systemMode == 'AUTOMATIC';

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1C1E),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: isOn ? Colors.green.withOpacity(0.5) : Colors.transparent),
      ),
      child: Row(
        children: [
          Icon(
            Icons.settings_applications,
            color: isOn ? Colors.green : Colors.grey,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(name, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w500)),
                Text(
                  isOn ? 'Running' : 'Stopped',
                  style: TextStyle(color: isOn ? Colors.green : Colors.grey, fontSize: 12),
                ),
              ],
            ),
          ),
          Switch(
            value: isOn,
            onChanged: isAuto ? null : (val) => _toggleMotor(id, val),
            activeColor: Colors.green,
          ),
        ],
      ),
    );
  }

  Widget _buildRecentReadings() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF212529),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Recent Readings',
                style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
              ),
              GestureDetector(
                onTap: () => Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const HistoryScreen()),
                ),
                child: const Text('View All →', style: TextStyle(color: Color(0xFF4CAF50))),
              ),
            ],
          ),
          const SizedBox(height: 12),
          if (_recentReadings.isEmpty)
            const Text('No readings yet', style: TextStyle(color: Colors.white54))
          else
            ..._recentReadings.take(5).map((reading) => _buildReadingTile(reading)),
        ],
      ),
    );
  }

  Widget _buildReadingTile(Map<String, dynamic> reading) {
    final value = double.tryParse(reading['value'].toString()) ?? 0;
    final nodeId = reading['nodeid'] ?? 'Unknown';
    final timestamp = reading['timestamp'] ?? '';
    
    // Parse timestamp
    String timeStr = '';
    try {
      final dt = DateTime.parse(timestamp);
      timeStr = '${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';
    } catch (_) {
      timeStr = timestamp.toString().substring(11, 16);
    }

    Color valueColor = Colors.green;
    if (value < 30) valueColor = Colors.red;
    else if (value > 70) valueColor = Colors.blue;

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1C1E),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Container(
            width: 50,
            height: 50,
            decoration: BoxDecoration(
              color: valueColor.withOpacity(0.2),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Center(
              child: Text(
                '${value.toInt()}%',
                style: TextStyle(color: valueColor, fontWeight: FontWeight.bold),
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(nodeId, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w500)),
                Text(timeStr, style: TextStyle(color: Colors.white.withOpacity(0.5), fontSize: 12)),
              ],
            ),
          ),
          Text(
            reading['moisture_status'] ?? '',
            style: TextStyle(color: valueColor, fontSize: 12),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActions() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Quick Actions',
          style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(child: _buildActionCard('Devices', Icons.devices, Colors.blue, () {
              Navigator.push(context, MaterialPageRoute(builder: (_) => const DeviceListScreen()));
            })),
            const SizedBox(width: 12),
            Expanded(child: _buildActionCard('Motors', Icons.settings_applications, Colors.green, () {
              Navigator.push(context, MaterialPageRoute(builder: (_) => const MotorsScreen()));
            })),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(child: _buildActionCard('Moisture', Icons.water_drop, Colors.cyan, () {
              Navigator.push(context, MaterialPageRoute(builder: (_) => const SoilMoistureScreen()));
            })),
            const SizedBox(width: 12),
            Expanded(child: _buildActionCard('History', Icons.history, Colors.orange, () {
              Navigator.push(context, MaterialPageRoute(builder: (_) => const HistoryScreen()));
            })),
          ],
        ),
      ],
    );
  }

  Widget _buildActionCard(String title, IconData icon, Color color, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: const Color(0xFF212529),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: color.withOpacity(0.2),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: color, size: 28),
            ),
            const SizedBox(height: 12),
            Text(title, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w500)),
          ],
        ),
      ),
    );
  }
}
