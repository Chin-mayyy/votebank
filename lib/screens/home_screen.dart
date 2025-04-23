import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final TextEditingController _questionController = TextEditingController();
  String _response = '';
  bool _isLoading = false;
  String? _errorMessage;
  Map<String, dynamic>? _debugInfo;

  Future<void> _sendQuery() async {
    if (_questionController.text.isEmpty) {
      setState(() {
        _errorMessage = 'Please enter a question';
        _debugInfo = null;
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _response = '';
      _errorMessage = null;
      _debugInfo = null;
    });

    try {
      final response = await http.post(
        Uri.parse('http://localhost:8000/api/query'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'question': _questionController.text}),
      );

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);
        setState(() {
          _response = responseData['response'] ?? 'No response received';
        });
      } else {
        final errorData = jsonDecode(response.body);
        setState(() {
          _errorMessage = _getErrorMessage(errorData['error'] ?? 'Unknown error occurred');
          _debugInfo = errorData['debug_info'];
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = _getErrorMessage(e.toString());
        _debugInfo = {'raw_error': e.toString()};
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  String _getErrorMessage(String error) {
    if (error.contains('API key')) {
      return 'Server configuration error: Please check API keys';
    } else if (error.contains('connection')) {
      return 'Unable to connect to server. Please make sure the backend is running.';
    } else if (error.contains('database')) {
      return 'Database connection error. Please try again later.';
    } else {
      return 'An error occurred: ${error.split(':').last.trim()}';
    }
  }

  Widget _buildDebugInfo() {
    if (_debugInfo == null) return const SizedBox.shrink();

    return Card(
      color: Colors.red.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Debug Information:',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: Colors.red,
              ),
            ),
            const SizedBox(height: 8),
            ..._debugInfo!.entries.map((entry) {
              return Padding(
                padding: const EdgeInsets.only(bottom: 8.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${entry.key}:',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    Text(
                      entry.value.toString(),
                      style: const TextStyle(fontFamily: 'monospace'),
                    ),
                  ],
                ),
              );
            }).toList(),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('VoteBank Q&A'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _questionController,
              decoration: InputDecoration(
                hintText: 'Ask your question about voting data...',
                border: const OutlineInputBorder(),
                errorText: _errorMessage,
              ),
              maxLines: 3,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _isLoading ? null : _sendQuery,
              child: _isLoading
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                      ),
                    )
                  : const Text('Get Answer'),
            ),
            const SizedBox(height: 24),
            if (_debugInfo != null) _buildDebugInfo(),
            if (_response.isNotEmpty)
              Expanded(
                child: Card(
                  elevation: 2,
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: SingleChildScrollView(
                      child: Text(
                        _response,
                        style: const TextStyle(fontSize: 16),
                      ),
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _questionController.dispose();
    super.dispose();
  }
} 