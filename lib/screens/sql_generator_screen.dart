import 'package:flutter/material.dart';
import '../models/sql_response.dart';
import '../services/vanna_service.dart';

class SQLGeneratorScreen extends StatefulWidget {
  final VannaService vannaService;

  const SQLGeneratorScreen({
    super.key,
    required this.vannaService,
  });

  @override
  State<SQLGeneratorScreen> createState() => _SQLGeneratorScreenState();
}

class _SQLGeneratorScreenState extends State<SQLGeneratorScreen> {
  final TextEditingController _promptController = TextEditingController();
  SQLResponse _response = SQLResponse(sql: '');

  Future<void> _generateSQL() async {
    setState(() {
      _response = _response.copyWith(isLoading: true, error: null);
    });

    try {
      final sql = await widget.vannaService.generateSQL(_promptController.text);
      setState(() {
        _response = SQLResponse(sql: sql);
      });
    } catch (e) {
      setState(() {
        _response = SQLResponse(sql: '', error: e.toString());
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('SQL Generator'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextField(
              controller: _promptController,
              decoration: const InputDecoration(
                labelText: 'Enter your prompt',
                border: OutlineInputBorder(),
              ),
              maxLines: 3,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _response.isLoading ? null : _generateSQL,
              child: _response.isLoading
                  ? const CircularProgressIndicator()
                  : const Text('Generate SQL'),
            ),
            const SizedBox(height: 24),
            if (_response.error != null)
              Container(
                padding: const EdgeInsets.all(8),
                color: Colors.red[100],
                child: Text(
                  _response.error!,
                  style: const TextStyle(color: Colors.red),
                ),
              ),
            if (_response.sql.isNotEmpty) ...[
              const Text(
                'Generated SQL:',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey[200],
                  borderRadius: BorderRadius.circular(8),
                ),
                child: SelectableText(
                  _response.sql,
                  style: const TextStyle(fontFamily: 'monospace'),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _promptController.dispose();
    super.dispose();
  }
} 