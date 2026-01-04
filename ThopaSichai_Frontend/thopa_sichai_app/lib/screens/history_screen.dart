import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:intl/intl.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  List<dynamic> _historyData = [];
  bool _isLoading = true;
  String _errorMessage = '';
  String _selectedFilter = 'All Time';

  @override
  void initState() {
    super.initState();
    _fetchHistory();
  }

  Future<void> _fetchHistory() async {
    if (!mounted) return;
    setState(() {
      _isLoading = true;
      _errorMessage = '';
    });

    try {
      final response = await http.get(
        Uri.parse('http://192.168.16.112:8000/api/data/?page_size=100&ordering=-timestamp'),
      ).timeout(const Duration(seconds: 20));

      if (!mounted) return;
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        // API returns {"success": true, "data": {"records": [...]}}
        List records = [];
        if (data['data'] != null && data['data']['records'] != null) {
          records = data['data']['records'];
        } else if (data['results'] != null) {
          records = data['results'];
        }
        if (mounted) {
          setState(() {
            _historyData = records;
            _isLoading = false;
          });
        }
      } else {
        if (mounted) {
          setState(() {
            _errorMessage = 'Failed to load history';
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

  String _formatDateTime(String? dateTimeStr) {
    if (dateTimeStr == null) return 'N/A';
    try {
      final dateTime = DateTime.parse(dateTimeStr);
      return DateFormat('MMM dd, yyyy • HH:mm').format(dateTime.toLocal());
    } catch (e) {
      return dateTimeStr;
    }
  }

  Color _getMoistureColor(dynamic value) {
    if (value == null) return Colors.grey;
    try {
      final level = double.parse(value.toString());
      if (level < 30) return Colors.red.shade400;
      if (level < 50) return Colors.orange.shade400;
      if (level < 70) return Colors.yellow.shade700;
      return Colors.green.shade400;
    } catch (e) {
      return Colors.grey;
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
          'Reading History',
          style: TextStyle(
            color: Colors.white,
            fontSize: 20,
            fontWeight: FontWeight.w600,
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.white),
            onPressed: _fetchHistory,
          ),
        ],
      ),
      body: Column(
        children: [
          // Filter Chips
          Container(
            padding: const EdgeInsets.all(16),
            color: const Color(0xFF212529),
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: [
                  _buildFilterChip('24 Hours'),
                  const SizedBox(width: 8),
                  _buildFilterChip('7 Days'),
                  const SizedBox(width: 8),
                  _buildFilterChip('30 Days'),
                  const SizedBox(width: 8),
                  _buildFilterChip('All Time'),
                ],
              ),
            ),
          ),
          // History List
          Expanded(
            child: _isLoading
                ? const Center(
                    child: CircularProgressIndicator(color: Colors.green),
                  )
                : _errorMessage.isNotEmpty
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.error_outline, size: 64, color: Colors.red.shade300),
                            const SizedBox(height: 16),
                            Text(_errorMessage, style: const TextStyle(color: Colors.white)),
                            ElevatedButton(
                              onPressed: _fetchHistory,
                              child: const Text('Retry'),
                            ),
                          ],
                        ),
                      )
                    : _historyData.isEmpty
                        ? const Center(
                            child: Text(
                              'No history data',
                              style: TextStyle(color: Colors.white),
                            ),
                          )
                        : ListView.builder(
                            padding: const EdgeInsets.all(16),
                            itemCount: _historyData.length,
                            itemBuilder: (context, index) {
                              final record = _historyData[index];
                              return _buildHistoryCard(record);
                            },
                          ),
          ),
        ],
      ),
    );
  }

  Widget _buildFilterChip(String label) {
    final isSelected = _selectedFilter == label;
    return FilterChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (selected) {
        setState(() {
          _selectedFilter = label;
        });
      },
      backgroundColor: const Color(0xFF1A1C1E),
      selectedColor: const Color(0xFF82E0AA),
      labelStyle: TextStyle(
        color: isSelected ? Colors.black : Colors.white,
        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
      ),
    );
  }

  Widget _buildHistoryCard(Map<String, dynamic> record) {
    final nodeid = record['nodeid'] ?? 'Unknown';
    final value = record['value'];
    final timestamp = record['timestamp'];
    final ipAddress = record['ip_address'] ?? 'N/A';

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF212529),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: _getMoistureColor(value).withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: _getMoistureColor(value).withOpacity(0.2),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(
              Icons.water_drop,
              color: _getMoistureColor(value),
              size: 24,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      nodeid,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 14,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    Text(
                      '${value?.toString() ?? 'N/A'}%',
                      style: TextStyle(
                        color: _getMoistureColor(value),
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                Text(
                  _formatDateTime(timestamp),
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.6),
                    fontSize: 12,
                  ),
                ),
                Text(
                  'IP: $ipAddress',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.4),
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
