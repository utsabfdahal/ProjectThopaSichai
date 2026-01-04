import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  // Backend server URL
  static const String baseUrl = 'http://192.168.16.112:8000';
  
  // Timeout duration for API requests (20 seconds for slow networks)
  static const Duration requestTimeout = Duration(seconds: 20);

  // ============== AUTHENTICATION ==============

  /// Login user with username and password
  static Future<Map<String, dynamic>> login(String username, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/auth/login/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'username': username, 'password': password}),
      ).timeout(requestTimeout);

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else if (response.statusCode == 401) {
        throw Exception('Invalid username or password');
      } else {
        throw Exception('Login failed: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  /// Register new user
  static Future<Map<String, dynamic>> register({
    required String username,
    required String email,
    required String password,
    required String password2,
    String? firstName,
    String? lastName,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/auth/register/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'username': username,
          'email': email,
          'password': password,
          'password2': password2,
          if (firstName != null) 'first_name': firstName,
          if (lastName != null) 'last_name': lastName,
        }),
      ).timeout(requestTimeout);

      if (response.statusCode == 201) {
        return jsonDecode(response.body);
      } else {
        final errors = jsonDecode(response.body);
        throw Exception(errors.values.first.toString());
      }
    } catch (e) {
      throw Exception('Registration failed: $e');
    }
  }

  /// Get user profile
  static Future<Map<String, dynamic>> getProfile(String token) async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/auth/profile/'),
      headers: {'Authorization': 'Token $token'},
    ).timeout(requestTimeout);

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to get profile');
  }

  /// Logout user
  static Future<void> logout(String token) async {
    await http.post(
      Uri.parse('$baseUrl/api/auth/logout/'),
      headers: {'Authorization': 'Token $token'},
    ).timeout(requestTimeout);
  }

  // ============== SOIL MOISTURE DATA ==============

  /// Get soil moisture records with pagination
  /// GET /api/data/?page=1&page_size=100
  static Future<List<dynamic>> getSoilMoistureData({int page = 1, int pageSize = 100}) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/data/?page=$page&page_size=$pageSize'),
      ).timeout(requestTimeout);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        // Handle response format: {"success": true, "data": {"records": [...]}}
        if (data['success'] == true && data['data'] != null) {
          return data['data']['records'] ?? [];
        }
        return data is List ? data : [];
      }
      throw Exception('Failed to fetch data');
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  /// Get latest soil moisture reading
  /// GET /api/data/latest/?nodeid=xxx
  static Future<Map<String, dynamic>> getLatestMoisture({String? nodeid}) async {
    try {
      String url = '$baseUrl/api/data/latest/';
      if (nodeid != null) url += '?nodeid=$nodeid';
      
      final response = await http.get(Uri.parse(url)).timeout(requestTimeout);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['success'] == true && data['data'] != null) {
          return data['data'];
        }
        return data;
      }
      throw Exception('Failed to fetch latest data');
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  /// Get filtered soil moisture data
  /// GET /api/data/filtered/?start_date=...&end_date=...&nodeid=...
  static Future<List<dynamic>> getFilteredData({
    DateTime? startDate,
    DateTime? endDate,
    String? nodeid,
    int page = 1,
    int pageSize = 100,
  }) async {
    try {
      final params = <String, String>{
        'page': page.toString(),
        'page_size': pageSize.toString(),
      };
      if (startDate != null) params['start_date'] = startDate.toIso8601String();
      if (endDate != null) params['end_date'] = endDate.toIso8601String();
      if (nodeid != null) params['nodeid'] = nodeid;

      final uri = Uri.parse('$baseUrl/api/data/filtered/').replace(queryParameters: params);
      final response = await http.get(uri).timeout(requestTimeout);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['success'] == true && data['data'] != null) {
          return data['data']['records'] ?? [];
        }
        return data is List ? data : [];
      }
      throw Exception('Failed to fetch filtered data');
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  /// Send sensor data (for testing/simulation)
  /// POST /api/data/receive/
  static Future<Map<String, dynamic>> sendSensorData({
    required String nodeid,
    required double value,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/data/receive/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'nodeid': nodeid, 'value': value}),
      ).timeout(requestTimeout);

      if (response.statusCode == 201) {
        return jsonDecode(response.body);
      }
      throw Exception('Failed to send data');
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  // ============== MOTORS ==============

  /// Get all motors
  /// GET /api/motors/
  /// Response format: {"success": true, "data": {"motors": [...]}}
  static Future<List<dynamic>> getMotors() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/motors/'),
      ).timeout(requestTimeout);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        // API returns {"success": true, "data": {"motors": [...]}}
        if (data['success'] == true && data['data'] != null) {
          final motorsData = data['data'];
          if (motorsData['motors'] != null) {
            return motorsData['motors'] as List;
          }
          return motorsData is List ? motorsData : [];
        }
        return data is List ? data : [];
      }
      throw Exception('Failed to fetch motors');
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  /// Create a new motor
  /// POST /api/motors/
  static Future<Map<String, dynamic>> createMotor({
    required String name,
    String? sensorNodeid,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/motors/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'name': name,
          if (sensorNodeid != null) 'sensor_nodeid': sensorNodeid,
        }),
      ).timeout(requestTimeout);

      if (response.statusCode == 201) {
        return jsonDecode(response.body);
      }
      throw Exception('Failed to create motor');
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  /// Get single motor by ID
  /// GET /api/motors/{motor_id}/
  static Future<Map<String, dynamic>> getMotor(int motorId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/motors/$motorId/'),
      ).timeout(requestTimeout);

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      throw Exception('Failed to fetch motor');
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  /// Control motor (ON/OFF)
  /// POST /api/motors/{motor_id}/control/
  static Future<Map<String, dynamic>> controlMotor(int motorId, bool turnOn) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/motors/$motorId/control/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'name': 'Motor $motorId',
          'state': turnOn ? 'ON' : 'OFF',
        }),
      ).timeout(requestTimeout);

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      throw Exception('Failed to control motor');
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  /// Delete a motor
  /// DELETE /api/motors/{motor_id}/
  static Future<void> deleteMotor(int motorId) async {
    try {
      final response = await http.delete(
        Uri.parse('$baseUrl/api/motors/$motorId/'),
      ).timeout(requestTimeout);

      if (response.statusCode != 204 && response.statusCode != 200) {
        throw Exception('Failed to delete motor');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  /// Get simple motor status info
  /// GET /api/motorsinfo/
  static Future<Map<String, dynamic>> getMotorsInfo() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/motorsinfo/'),
      ).timeout(requestTimeout);

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      throw Exception('Failed to fetch motors info');
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  // ============== SYSTEM MODE ==============

  /// Get current system mode (MANUAL or AUTOMATIC)
  /// GET /api/mode/
  static Future<Map<String, dynamic>> getSystemMode() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/mode/'),
      ).timeout(requestTimeout);

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      throw Exception('Failed to fetch mode');
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  /// Set system mode
  /// POST /api/mode/set/
  static Future<Map<String, dynamic>> setSystemMode(String mode) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/mode/set/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'mode': mode}),
      ).timeout(requestTimeout);

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      throw Exception('Failed to set mode');
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  // ============== THRESHOLD CONFIG ==============

  /// Get threshold configurations
  /// GET /api/config/thresholds/
  static Future<Map<String, dynamic>> getThresholds() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/config/thresholds/'),
      ).timeout(requestTimeout);

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      throw Exception('Failed to fetch thresholds');
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  /// Set threshold configuration for a node
  /// POST /api/config/thresholds/set/
  /// threshold: Motor turns ON when moisture value drops below this threshold
  static Future<Map<String, dynamic>> setThreshold({
    required String nodeid,
    required double threshold,
  }) async {
    try {
      final body = {
        'nodeid': nodeid,
        'threshold': threshold,
      };

      final response = await http.post(
        Uri.parse('$baseUrl/api/config/thresholds/set/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(body),
      ).timeout(requestTimeout);

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      throw Exception('Failed to set threshold');
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  // ============== DASHBOARD & STATUS ==============

  /// Get dashboard statistics
  /// GET /api/stats/dashboard/
  static Future<Map<String, dynamic>> getDashboardStats() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/stats/dashboard/'),
      ).timeout(requestTimeout);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['success'] == true && data['data'] != null) {
          return data['data'];
        }
        return data;
      }
      throw Exception('Failed to fetch dashboard stats');
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  /// Get combined system status
  /// GET /api/status/
  static Future<Map<String, dynamic>> getSystemStatus() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/status/'),
      ).timeout(requestTimeout);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['success'] == true && data['data'] != null) {
          return data['data'];
        }
        return data;
      }
      throw Exception('Failed to fetch status');
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  /// Health check
  /// GET /api/health/
  static Future<Map<String, dynamic>> healthCheck() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/health/'),
      ).timeout(requestTimeout);

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      throw Exception('Health check failed');
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  // ============== HELPER METHODS ==============

  /// Get average of last N soil moisture readings
  static Future<double> getAverageMoisture({int count = 10}) async {
    try {
      final records = await getSoilMoistureData(pageSize: count);
      if (records.isEmpty) return 0.0;
      
      double sum = 0;
      int validCount = 0;
      for (var record in records) {
        try {
          sum += double.parse(record['value'].toString());
          validCount++;
        } catch (_) {}
      }
      return validCount > 0 ? sum / validCount : 0.0;
    } catch (e) {
      return 0.0;
    }
  }

  /// Get unique sensor node IDs from recent data
  static Future<List<String>> getUniqueNodeIds() async {
    try {
      final records = await getSoilMoistureData(pageSize: 100);
      final nodeIds = <String>{};
      for (var record in records) {
        if (record['nodeid'] != null) {
          nodeIds.add(record['nodeid'].toString());
        }
      }
      return nodeIds.toList();
    } catch (e) {
      return [];
    }
  }
}
