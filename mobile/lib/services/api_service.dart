import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  String baseUrl = 'http://localhost:19951';
  String? _token;

  Map<String, String> get _headers => {
    'Content-Type': 'application/json',
    if (_token != null) 'Authorization': 'Bearer $_token',
  };

  Future<Map<String, dynamic>?> get(String path) async {
    try {
      final r = await http.get(Uri.parse('$baseUrl$path'), headers: _headers).timeout(const Duration(seconds: 5));
      if (r.statusCode == 200) return jsonDecode(r.body);
    } catch (_) {}
    return null;
  }

  Future<Map<String, dynamic>?> post(String path, Map<String, dynamic> body) async {
    try {
      final r = await http.post(Uri.parse('$baseUrl$path'), headers: _headers, body: jsonEncode(body)).timeout(const Duration(seconds: 30));
      if (r.statusCode == 200) return jsonDecode(r.body);
    } catch (_) {}
    return null;
  }

  Future<bool> login(String password) async {
    final r = await post('/api/login', {'password': password});
    if (r != null && r['token'] != null) {
      _token = r['token'];
      return true;
    }
    return false;
  }

  Future<Map<String, dynamic>?> getDashboard() => get('/api/dashboard');
  Future<Map<String, dynamic>?> getMemory() => get('/api/memory');
  Future<Map<String, dynamic>?> getTasks() => get('/api/tasks/queue');
  Future<Map<String, dynamic>?> sendCommand(String msg) => post('/api/command', {'command': msg});
  Future<Map<String, dynamic>?> chatWithAI(String msg) => post('/api/command/panel', {'message': msg});
}
