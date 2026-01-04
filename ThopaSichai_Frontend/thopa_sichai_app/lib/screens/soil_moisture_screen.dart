import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/foundation.dart' show kIsWeb;

class SoilMoistureScreen extends StatefulWidget {
  const SoilMoistureScreen({super.key});

  @override
  State<SoilMoistureScreen> createState() => _SoilMoistureScreenState();
}

class _SoilMoistureScreenState extends State<SoilMoistureScreen> {
  List<dynamic> _moistureData = [];
  bool _isLoading = true;
  String _errorMessage = '';
  String _selectedPeriod = '24H';
  
  // Use the same IP for both web and mobile
  static const String _baseUrl = 'http://192.168.16.112:8000';

  @override
  void initState() {
    super.initState();
    _fetchMoistureData();
  }

  Future<void> _fetchMoistureData() async {
    if (!mounted) return;
    setState(() {
      _isLoading = true;
      _errorMessage = '';
    });

    try {
      // Fetch more data and order by timestamp descending to get most recent first
      final response = await http.get(
        Uri.parse('$_baseUrl/api/data/?page_size=200&ordering=-timestamp'),
      ).timeout(const Duration(seconds: 20));

      if (!mounted) return;
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        // API returns {"success": true, "data": {"records": [...]}}
        List records = [];
        if (data is List) {
          records = data;
        } else if (data['data'] != null && data['data']['records'] != null) {
          records = data['data']['records'];
        } else if (data['results'] != null) {
          records = data['results'];
        }
        if (mounted) {
          setState(() {
            _moistureData = records;
            _isLoading = false;
          });
        }
      } else {
        if (mounted) {
          setState(() {
            _errorMessage = 'Failed to load data: ${response.statusCode}';
            _isLoading = false;
          });
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = 'Error: $e';
          _isLoading = false;
        });
      }
    }
  }

  double get _currentReading {
    if (_moistureData.isEmpty) return 0;
    try {
      return double.parse(_moistureData.first['value'].toString());
    } catch (e) {
      return 0;
    }
  }

  double get _highValue {
    if (_moistureData.isEmpty) return 0;
    double max = 0;
    for (var item in _moistureData) {
      try {
        double val = double.parse(item['value'].toString());
        if (val > max) max = val;
      } catch (e) {}
    }
    return max;
  }

  double get _lowValue {
    if (_moistureData.isEmpty) return 0;
    double min = 100;
    for (var item in _moistureData) {
      try {
        double val = double.parse(item['value'].toString());
        if (val < min) min = val;
      } catch (e) {}
    }
    return min;
  }

  double get _avgValue {
    if (_moistureData.isEmpty) return 0;
    double sum = 0;
    int count = 0;
    for (var item in _moistureData) {
      try {
        sum += double.parse(item['value'].toString());
        count++;
      } catch (e) {}
    }
    return count > 0 ? sum / count : 0;
  }

  // Get chart data - show all data from oldest (left) to newest (right)
  List<FlSpot> _getChartData() {
    if (_moistureData.isEmpty) return [];
    List<FlSpot> spots = [];
    
    // Filter data based on selected period
    List<dynamic> filteredData = _filterDataByPeriod();
    
    // Sort by timestamp ascending (oldest first for left-to-right chart)
    filteredData.sort((a, b) {
      try {
        final aTime = DateTime.parse(a['timestamp'] ?? a['created_at'] ?? '');
        final bTime = DateTime.parse(b['timestamp'] ?? b['created_at'] ?? '');
        return aTime.compareTo(bTime);
      } catch (_) {
        return 0;
      }
    });
    
    // Create spots for chart (limit to 100 for performance)
    final dataToShow = filteredData.length > 100 
        ? filteredData.sublist(filteredData.length - 100) 
        : filteredData;
    
    for (int i = 0; i < dataToShow.length; i++) {
      try {
        double value = double.parse(dataToShow[i]['value'].toString());
        spots.add(FlSpot(i.toDouble(), value));
      } catch (e) {}
    }
    return spots;
  }
  
  // Filter data by selected time period
  List<dynamic> _filterDataByPeriod() {
    if (_moistureData.isEmpty) return [];
    
    final now = DateTime.now();
    Duration? duration;
    
    switch (_selectedPeriod) {
      case '24H':
        duration = const Duration(hours: 24);
        break;
      case '7D':
        duration = const Duration(days: 7);
        break;
      case '30D':
        duration = const Duration(days: 30);
        break;
      case 'All Time':
      default:
        return List.from(_moistureData);
    }
    
    final cutoff = now.subtract(duration);
    return _moistureData.where((item) {
      try {
        final timestamp = DateTime.parse(item['timestamp'] ?? item['created_at'] ?? '');
        return timestamp.isAfter(cutoff);
      } catch (_) {
        return true;
      }
    }).toList();
  }

  // Get timestamps for X-axis labels - matches _getChartData order
  List<String> _getTimeLabels() {
    if (_moistureData.isEmpty) return [];
    List<String> labels = [];
    
    // Filter data based on selected period
    List<dynamic> filteredData = _filterDataByPeriod();
    
    // Sort by timestamp ascending (oldest first)
    filteredData.sort((a, b) {
      try {
        final aTime = DateTime.parse(a['timestamp'] ?? a['created_at'] ?? '');
        final bTime = DateTime.parse(b['timestamp'] ?? b['created_at'] ?? '');
        return aTime.compareTo(bTime);
      } catch (_) {
        return 0;
      }
    });
    
    // Limit to last 100 like chart data
    final dataToShow = filteredData.length > 100 
        ? filteredData.sublist(filteredData.length - 100) 
        : filteredData;
    
    for (int i = 0; i < dataToShow.length; i++) {
      try {
        final timestamp = dataToShow[i]['timestamp'] ?? dataToShow[i]['created_at'];
        if (timestamp != null) {
          final dt = DateTime.parse(timestamp);
          labels.add('${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}');
        } else {
          labels.add('');
        }
      } catch (e) {
        labels.add('');
      }
    }
    return labels;
  }

  List<FlSpot> _getChartDataOld() {
    if (_moistureData.isEmpty) return [];
    List<FlSpot> spots = [];
    for (int i = 0; i < _moistureData.length; i++) {
      try {
        double value = double.parse(_moistureData[i]['value'].toString());
        spots.add(FlSpot(i.toDouble(), value));
      } catch (e) {}
    }
    return spots;
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
          'Soil Moisture',
          style: TextStyle(
            color: Colors.white,
            fontSize: 20,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      body: _isLoading
          ? const Center(
              child: CircularProgressIndicator(
                color: Colors.green,
              ),
            )
          : _errorMessage.isNotEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.error_outline,
                        size: 64,
                        color: Colors.red.shade300,
                      ),
                      const SizedBox(height: 16),
                      Text(
                        _errorMessage,
                        style: const TextStyle(color: Colors.white),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: _fetchMoistureData,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.green.shade700,
                        ),
                        child: const Text('Retry'),
                      ),
                    ],
                  ),
                )
              : _moistureData.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.water_drop_outlined,
                            size: 64,
                            color: Colors.grey.shade600,
                          ),
                          const SizedBox(height: 16),
                          Text(
                            'No soil moisture data yet',
                            style: TextStyle(
                              color: Colors.grey.shade400,
                              fontSize: 18,
                            ),
                          ),
                        ],
                      ),
                    )
                  : SingleChildScrollView(
                      padding: const EdgeInsets.all(20),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // Current Reading
                          const Text(
                            'Current Reading',
                            style: TextStyle(
                              color: Colors.grey,
                              fontSize: 14,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            '${_currentReading.toInt()}%',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 48,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 32),

                          // Chart Title
                          const Text(
                            'Moisture Readings Over Time',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            '${_moistureData.length} readings',
                            style: TextStyle(
                              color: Colors.grey.shade500,
                              fontSize: 12,
                            ),
                          ),
                          const SizedBox(height: 16),

                          // Chart
                          Container(
                            height: 280,
                            padding: const EdgeInsets.fromLTRB(8, 16, 16, 8),
                            decoration: BoxDecoration(
                              color: const Color(0xFF212529),
                              borderRadius: BorderRadius.circular(16),
                            ),
                            child: LineChart(
                              LineChartData(
                                gridData: FlGridData(
                                  show: true,
                                  drawVerticalLine: false,
                                  horizontalInterval: 20,
                                  getDrawingHorizontalLine: (value) {
                                    return FlLine(
                                      color: Colors.grey.shade800,
                                      strokeWidth: 1,
                                    );
                                  },
                                ),
                                titlesData: FlTitlesData(
                                  show: true,
                                  bottomTitles: AxisTitles(
                                    sideTitles: SideTitles(
                                      showTitles: true,
                                      reservedSize: 30,
                                      interval: (_getChartData().length / 5).clamp(1, 10).toDouble(),
                                      getTitlesWidget: (value, meta) {
                                        final labels = _getTimeLabels();
                                        final idx = value.toInt();
                                        if (idx >= 0 && idx < labels.length) {
                                          return Padding(
                                            padding: const EdgeInsets.only(top: 8),
                                            child: Text(
                                              labels[idx],
                                              style: TextStyle(
                                                color: Colors.grey.shade500,
                                                fontSize: 10,
                                              ),
                                            ),
                                          );
                                        }
                                        return const Text('');
                                      },
                                    ),
                                  ),
                                  leftTitles: AxisTitles(
                                    sideTitles: SideTitles(
                                      showTitles: true,
                                      reservedSize: 40,
                                      interval: 25,
                                      getTitlesWidget: (value, meta) {
                                        return Text(
                                          '${value.toInt()}%',
                                          style: TextStyle(
                                            color: Colors.grey.shade500,
                                            fontSize: 10,
                                          ),
                                        );
                                      },
                                    ),
                                  ),
                                  topTitles: const AxisTitles(
                                    sideTitles: SideTitles(showTitles: false),
                                  ),
                                  rightTitles: const AxisTitles(
                                    sideTitles: SideTitles(showTitles: false),
                                  ),
                                ),
                                borderData: FlBorderData(show: false),
                                minY: 0,
                                maxY: 100,
                                lineBarsData: [
                                  LineChartBarData(
                                    spots: _getChartData(),
                                    isCurved: true,
                                    color: const Color(0xFF4FC3F7),
                                    barWidth: 2,
                                    isStrokeCapRound: true,
                                    dotData: const FlDotData(show: false),
                                    belowBarData: BarAreaData(
                                      show: true,
                                      color: const Color(0xFF4FC3F7).withOpacity(0.2),
                                    ),
                                  ),
                                ],
                                lineTouchData: LineTouchData(
                                  touchTooltipData: LineTouchTooltipData(
                                    getTooltipItems: (touchedSpots) {
                                      return touchedSpots.map((spot) {
                                        final labels = _getTimeLabels();
                                        final idx = spot.x.toInt();
                                        final time = idx < labels.length ? labels[idx] : '';
                                        return LineTooltipItem(
                                          '${spot.y.toStringAsFixed(1)}%\n$time',
                                          const TextStyle(
                                            color: Colors.white,
                                            fontWeight: FontWeight.bold,
                                          ),
                                        );
                                      }).toList();
                                    },
                                  ),
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(height: 24),

                          // Time Period Buttons
                          Row(
                            children: [
                              Expanded(
                                child: _periodButton('24H'),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: _periodButton('7D'),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: _periodButton('30D'),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: _periodButton('All Time'),
                              ),
                            ],
                          ),
                          const SizedBox(height: 32),

                          // Statistics
                          Row(
                            children: [
                              Expanded(
                                child: _statCard(
                                  'High',
                                  '${_highValue.toInt()}%',
                                  Icons.arrow_upward,
                                  Colors.red,
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: _statCard(
                                  'Average',
                                  '${_avgValue.toInt()}%',
                                  Icons.show_chart,
                                  Colors.blue,
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: _statCard(
                                  'Low',
                                  '${_lowValue.toInt()}%',
                                  Icons.arrow_downward,
                                  Colors.orange,
                                ),
                              ),
                            ],
                          ),
                          
                          const SizedBox(height: 24),
                          
                          // Recent Readings List
                          const Text(
                            'Recent Readings',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          const SizedBox(height: 12),
                          ..._buildRecentReadingsList(),
                        ],
                      ),
                    ),
    );
  }

  List<Widget> _buildRecentReadingsList() {
    final recent = _moistureData.take(10).toList();
    return recent.map((item) {
      final value = double.tryParse(item['value'].toString()) ?? 0;
      final timestamp = item['timestamp'] ?? item['created_at'];
      final nodeId = item['nodeid'] ?? 'Unknown';
      String timeStr = '';
      if (timestamp != null) {
        try {
          final dt = DateTime.parse(timestamp);
          timeStr = '${dt.day}/${dt.month} ${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';
        } catch (e) {}
      }
      
      return Container(
        margin: const EdgeInsets.only(bottom: 8),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: const Color(0xFF212529),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Row(
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: _getMoistureColor(value).withOpacity(0.2),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Center(
                child: Text(
                  '${value.toInt()}%',
                  style: TextStyle(
                    color: _getMoistureColor(value),
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Node: $nodeId',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  Text(
                    timeStr,
                    style: TextStyle(
                      color: Colors.grey.shade500,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ),
            Icon(
              Icons.water_drop,
              color: _getMoistureColor(value),
              size: 20,
            ),
          ],
        ),
      );
    }).toList();
  }

  Color _getMoistureColor(double value) {
    if (value < 30) return Colors.red;
    if (value < 50) return Colors.orange;
    if (value < 70) return Colors.green;
    return Colors.blue;
  }

  Widget _periodButton(String period) {
    bool isSelected = _selectedPeriod == period;
    return GestureDetector(
      onTap: () {
        setState(() {
          _selectedPeriod = period;
        });
      },
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFF4CAF50) : const Color(0xFF212529),
          borderRadius: BorderRadius.circular(24),
        ),
        child: Center(
          child: Text(
            period,
            style: TextStyle(
              color: Colors.white,
              fontSize: 14,
              fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
            ),
          ),
        ),
      ),
    );
  }

  Widget _statCard(String label, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF212529),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Icon(
            icon,
            color: color,
            size: 24,
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              color: color,
              fontSize: 22,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: TextStyle(
              color: Colors.grey.shade500,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }
}
