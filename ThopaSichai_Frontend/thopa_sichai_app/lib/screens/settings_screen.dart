import 'package:flutter/material.dart';
import '../services/api_service.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  // State
  bool _isLoading = true;
  bool _isSaving = false;
  String _systemMode = 'MANUAL';
  bool _enableNotifications = true;
  
  // Thresholds - one per node
  List<Map<String, dynamic>> _thresholds = [];
  Map<String, double> _thresholdValues = {};

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    setState(() => _isLoading = true);
    
    try {
      // Load thresholds and system mode in parallel
      final results = await Future.wait([
        ApiService.getThresholds().catchError((_) => <String, dynamic>{}),
        ApiService.getSystemMode().catchError((_) => <String, dynamic>{'mode': 'MANUAL'}),
      ]);

      final thresholdsResponse = results[0] as Map<String, dynamic>;
      final modeData = results[1] as Map<String, dynamic>;

      // Parse thresholds - API returns {"success": true, "data": {"thresholds": [...]}}
      List<Map<String, dynamic>> thresholds = [];
      if (thresholdsResponse['success'] == true && thresholdsResponse['data'] != null) {
        final data = thresholdsResponse['data'] as Map<String, dynamic>;
        if (data['thresholds'] != null) {
          thresholds = List<Map<String, dynamic>>.from(data['thresholds']);
        }
      }

      // Create threshold values map
      Map<String, double> thresholdValues = {};
      for (var t in thresholds) {
        final nodeId = t['nodeid'] as String? ?? '';
        final value = (t['threshold'] as num?)?.toDouble() ?? 50.0;
        thresholdValues[nodeId] = value;
      }

      if (mounted) {
        setState(() {
          _thresholds = thresholds;
          _thresholdValues = thresholdValues;
          _systemMode = modeData['mode'] ?? 'MANUAL';
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading settings: $e'), backgroundColor: Colors.red),
        );
      }
    }
  }

  Future<void> _saveThreshold(String nodeId, double value) async {
    setState(() => _isSaving = true);
    
    try {
      await ApiService.setThreshold(nodeid: nodeId, threshold: value);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Threshold for $nodeId saved: ${value.toInt()}%'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error saving: $e'), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isSaving = false);
      }
    }
  }

  Future<void> _saveAllThresholds() async {
    setState(() => _isSaving = true);
    
    try {
      for (var entry in _thresholdValues.entries) {
        await ApiService.setThreshold(nodeid: entry.key, threshold: entry.value);
      }
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('All thresholds saved successfully!'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error saving: $e'), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isSaving = false);
      }
    }
  }

  Future<void> _toggleSystemMode() async {
    final newMode = _systemMode == 'MANUAL' ? 'AUTOMATIC' : 'MANUAL';
    try {
      await ApiService.setSystemMode(newMode);
      if (mounted) {
        setState(() => _systemMode = newMode);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Mode changed to $newMode')),
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
        backgroundColor: const Color(0xFF212529),
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Settings',
          style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.w600),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.white),
            onPressed: _loadSettings,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // System Mode Section
                  _buildSectionTitle('System Mode'),
                  const SizedBox(height: 12),
                  _buildSystemModeCard(),
                  
                  const SizedBox(height: 24),
                  
                  // Moisture Thresholds Section
                  _buildSectionTitle('Moisture Thresholds'),
                  const SizedBox(height: 8),
                  Text(
                    'Set the moisture level at which each motor/pump will turn ON',
                    style: TextStyle(color: Colors.white.withOpacity(0.6), fontSize: 12),
                  ),
                  const SizedBox(height: 16),
                  
                  // Dynamic threshold cards for each node
                  if (_thresholds.isEmpty)
                    _buildNoThresholdsCard()
                  else
                    ..._thresholds.asMap().entries.map((entry) {
                      final index = entry.key;
                      final threshold = entry.value;
                      final nodeId = threshold['nodeid'] as String? ?? 'Unknown';
                      final value = _thresholdValues[nodeId] ?? 50.0;
                      return Padding(
                        padding: const EdgeInsets.only(bottom: 16),
                        child: _buildThresholdCard(
                          index: index + 1,
                          nodeId: nodeId,
                          value: value,
                          onChanged: (val) {
                            setState(() {
                              _thresholdValues[nodeId] = val;
                            });
                          },
                        ),
                      );
                    }),
                  
                  const SizedBox(height: 8),
                  
                  // Save All Button
                  if (_thresholds.isNotEmpty)
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        onPressed: _isSaving ? null : _saveAllThresholds,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF4CAF50),
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                        child: _isSaving
                            ? const SizedBox(
                                width: 24,
                                height: 24,
                                child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                              )
                            : const Text(
                                'Save All Thresholds',
                                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
                              ),
                      ),
                    ),
                  
                  const SizedBox(height: 24),
                  
                  // Notifications Section
                  _buildSectionTitle('Notifications'),
                  const SizedBox(height: 12),
                  _buildNotificationsCard(),
                  
                  const SizedBox(height: 24),
                  
                  // About Section
                  _buildSectionTitle('About'),
                  const SizedBox(height: 12),
                  _buildAboutCard(),
                  
                  const SizedBox(height: 40),
                ],
              ),
            ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: const TextStyle(
        color: Colors.white,
        fontSize: 18,
        fontWeight: FontWeight.w600,
      ),
    );
  }

  Widget _buildSystemModeCard() {
    final isAutomatic = _systemMode == 'AUTOMATIC';
    
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF212529),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isAutomatic ? Colors.green.withOpacity(0.3) : Colors.orange.withOpacity(0.3),
        ),
      ),
      child: Column(
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: isAutomatic ? Colors.green.withOpacity(0.2) : Colors.orange.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  isAutomatic ? Icons.auto_mode : Icons.touch_app,
                  color: isAutomatic ? Colors.green : Colors.orange,
                  size: 28,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      _systemMode,
                      style: TextStyle(
                        color: isAutomatic ? Colors.green : Colors.orange,
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      isAutomatic
                          ? 'Motors run automatically based on thresholds'
                          : 'You control motors manually',
                      style: TextStyle(color: Colors.white.withOpacity(0.7), fontSize: 12),
                    ),
                  ],
                ),
              ),
              Switch(
                value: isAutomatic,
                onChanged: (_) => _toggleSystemMode(),
                activeColor: Colors.green,
              ),
            ],
          ),
          if (isAutomatic) ...[
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.green.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  const Icon(Icons.info_outline, color: Colors.green, size: 20),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Motors will turn ON when moisture drops below the threshold value.',
                      style: TextStyle(color: Colors.green.withOpacity(0.8), fontSize: 12),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildNoThresholdsCard() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: const Color(0xFF212529),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        children: [
          Icon(Icons.settings_outlined, color: Colors.white.withOpacity(0.3), size: 48),
          const SizedBox(height: 12),
          Text(
            'No thresholds configured',
            style: TextStyle(color: Colors.white.withOpacity(0.6)),
          ),
          const SizedBox(height: 8),
          Text(
            'Add sensors to configure thresholds',
            style: TextStyle(color: Colors.white.withOpacity(0.4), fontSize: 12),
          ),
        ],
      ),
    );
  }

  Widget _buildThresholdCard({
    required int index,
    required String nodeId,
    required double value,
    required Function(double) onChanged,
  }) {
    // Colors based on index
    final colors = [Colors.blue, Colors.purple, Colors.teal, Colors.orange];
    final color = colors[(index - 1) % colors.length];
    
    // Determine status based on threshold
    String status;
    Color statusColor;
    if (value < 30) {
      status = 'Very Dry Trigger';
      statusColor = Colors.red;
    } else if (value < 50) {
      status = 'Dry Trigger';
      statusColor = Colors.orange;
    } else if (value < 70) {
      status = 'Normal Trigger';
      statusColor = Colors.green;
    } else {
      status = 'Wet Trigger';
      statusColor = Colors.blue;
    }
    
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF212529),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(Icons.water_drop, color: color),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Motor $index / Pump $index',
                      style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
                    ),
                    Text(
                      'Sensor: $nodeId',
                      style: TextStyle(color: Colors.white.withOpacity(0.6), fontSize: 12),
                    ),
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: statusColor.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  status,
                  style: TextStyle(color: statusColor, fontSize: 10, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 20),
          
          // Threshold value display
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Moisture Threshold',
                    style: TextStyle(color: Colors.white, fontWeight: FontWeight.w500),
                  ),
                  Text(
                    'Motor turns ON when moisture drops below this',
                    style: TextStyle(color: Colors.white.withOpacity(0.5), fontSize: 10),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: color.withOpacity(0.5)),
                ),
                child: Text(
                  '${value.toInt()}%',
                  style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 24),
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 12),
          
          // Slider
          SliderTheme(
            data: SliderTheme.of(context).copyWith(
              activeTrackColor: color,
              inactiveTrackColor: Colors.grey.shade700,
              thumbColor: color,
              overlayColor: color.withOpacity(0.2),
              trackHeight: 8,
              thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 12),
            ),
            child: Slider(
              value: value,
              min: 0,
              max: 100,
              divisions: 20,
              onChanged: onChanged,
            ),
          ),
          
          // Scale labels
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('0%', style: TextStyle(color: Colors.white.withOpacity(0.4), fontSize: 10)),
                Text('25%', style: TextStyle(color: Colors.white.withOpacity(0.4), fontSize: 10)),
                Text('50%', style: TextStyle(color: Colors.white.withOpacity(0.4), fontSize: 10)),
                Text('75%', style: TextStyle(color: Colors.white.withOpacity(0.4), fontSize: 10)),
                Text('100%', style: TextStyle(color: Colors.white.withOpacity(0.4), fontSize: 10)),
              ],
            ),
          ),
          
          const SizedBox(height: 16),
          
          // Visual indicator
          Container(
            height: 8,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(4),
              gradient: const LinearGradient(
                colors: [Colors.red, Colors.orange, Colors.yellow, Colors.green, Colors.blue],
              ),
            ),
            child: Stack(
              children: [
                Positioned(
                  left: (value / 100) * (MediaQuery.of(context).size.width - 104) - 2,
                  top: -4,
                  child: Container(
                    width: 4,
                    height: 16,
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(2),
                      boxShadow: [
                        BoxShadow(color: Colors.black.withOpacity(0.5), blurRadius: 4),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Dry', style: TextStyle(color: Colors.red.withOpacity(0.7), fontSize: 10)),
              Text('Wet', style: TextStyle(color: Colors.blue.withOpacity(0.7), fontSize: 10)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildNotificationsCard() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF212529),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.amber.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(Icons.notifications, color: Colors.amber),
              ),
              const SizedBox(width: 12),
              const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Push Notifications',
                    style: TextStyle(color: Colors.white, fontWeight: FontWeight.w500),
                  ),
                  Text(
                    'Get alerts for low moisture',
                    style: TextStyle(color: Colors.grey, fontSize: 12),
                  ),
                ],
              ),
            ],
          ),
          Switch(
            value: _enableNotifications,
            onChanged: (value) => setState(() => _enableNotifications = value),
            activeColor: const Color(0xFF4CAF50),
          ),
        ],
      ),
    );
  }

  Widget _buildAboutCard() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF212529),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        children: [
          _buildAboutRow('App Name', 'Thopa Sichai'),
          const Divider(color: Colors.grey, height: 24),
          _buildAboutRow('Version', '1.0.0'),
          const Divider(color: Colors.grey, height: 24),
          _buildAboutRow('Backend', 'http://192.168.16.112:8000'),
          const Divider(color: Colors.grey, height: 24),
          _buildAboutRow('Sensors', '${_thresholds.length}'),
        ],
      ),
    );
  }

  Widget _buildAboutRow(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: const TextStyle(color: Colors.grey)),
        Text(value, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w500)),
      ],
    );
  }
}
