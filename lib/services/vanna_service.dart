import 'dart:convert';
import 'package:http/http.dart' as http;

class VannaService {
  final String apiKey;
  final String baseUrl = 'https://api.vanna.ai/v1';
  final String? databaseUrl;
  final String? databaseType;
  final String? databaseUsername;
  final String? databasePassword;
  final String? databaseName;

  VannaService({
    required this.apiKey,
    this.databaseUrl,
    this.databaseType,
    this.databaseUsername,
    this.databasePassword,
    this.databaseName,
  });

  String _buildConnectionString() {
    switch (databaseType?.toLowerCase()) {
      case 'postgresql':
        return 'postgresql://$databaseUsername:$databasePassword@$databaseUrl/$databaseName';
      case 'mysql':
        return 'mysql://$databaseUsername:$databasePassword@$databaseUrl/$databaseName';
      case 'sqlite':
        return 'sqlite:///$databaseUrl';
      case 'mssql':
        return 'mssql://$databaseUsername:$databasePassword@$databaseUrl/$databaseName';
      default:
        throw Exception('Unsupported database type: $databaseType');
    }
  }

  Future<String> generateSQL(String prompt) async {
    try {
      final connectionString = _buildConnectionString();
      
      final response = await http.post(
        Uri.parse('$baseUrl/generate-sql'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $apiKey',
        },
        body: jsonEncode({
          'prompt': prompt,
          'database': {
            'type': databaseType,
            'connection_string': connectionString,
          },
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['sql'] ?? 'No SQL generated';
      } else {
        throw Exception('Failed to generate SQL: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error generating SQL: $e');
    }
  }
} 