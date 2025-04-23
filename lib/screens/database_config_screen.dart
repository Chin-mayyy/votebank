import 'package:flutter/material.dart';
import '../services/vanna_service.dart';
import 'sql_generator_screen.dart';

class DatabaseConfigScreen extends StatefulWidget {
  final String apiKey;

  const DatabaseConfigScreen({
    super.key,
    required this.apiKey,
  });

  @override
  State<DatabaseConfigScreen> createState() => _DatabaseConfigScreenState();
}

class _DatabaseConfigScreenState extends State<DatabaseConfigScreen> {
  final _formKey = GlobalKey<FormState>();
  final _databaseTypeController = TextEditingController();
  final _databaseUrlController = TextEditingController();
  final _databaseUsernameController = TextEditingController();
  final _databasePasswordController = TextEditingController();
  final _databaseNameController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Database Configuration'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: ListView(
            children: [
              DropdownButtonFormField<String>(
                decoration: const InputDecoration(
                  labelText: 'Database Type',
                  border: OutlineInputBorder(),
                ),
                items: const [
                  DropdownMenuItem(value: 'postgresql', child: Text('PostgreSQL')),
                  DropdownMenuItem(value: 'mysql', child: Text('MySQL')),
                  DropdownMenuItem(value: 'sqlite', child: Text('SQLite')),
                  DropdownMenuItem(value: 'mssql', child: Text('Microsoft SQL Server')),
                ],
                onChanged: (value) {
                  setState(() {
                    _databaseTypeController.text = value ?? '';
                    // Update hint text based on database type
                    if (value == 'postgresql') {
                      _databaseUrlController.text = 'localhost:5432';
                    } else if (value == 'mysql') {
                      _databaseUrlController.text = 'localhost:3306';
                    } else if (value == 'mssql') {
                      _databaseUrlController.text = 'localhost:1433';
                    }
                  });
                },
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please select a database type';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _databaseUrlController,
                decoration: const InputDecoration(
                  labelText: 'Database URL',
                  hintText: 'e.g., localhost:5432',
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter the database URL';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _databaseUsernameController,
                decoration: const InputDecoration(
                  labelText: 'Username',
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter the username';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _databasePasswordController,
                decoration: const InputDecoration(
                  labelText: 'Password',
                  border: OutlineInputBorder(),
                ),
                obscureText: true,
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter the password';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _databaseNameController,
                decoration: const InputDecoration(
                  labelText: 'Database Name',
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter the database name';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: _saveAndProceed,
                child: const Text('Save and Proceed'),
              ),
              const SizedBox(height: 16),
              const Card(
                child: Padding(
                  padding: EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Connection Help',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      SizedBox(height: 8),
                      Text('For PostgreSQL:'),
                      Text('• Default port: 5432'),
                      Text('• Example: localhost:5432'),
                      SizedBox(height: 8),
                      Text('For MySQL:'),
                      Text('• Default port: 3306'),
                      Text('• Example: localhost:3306'),
                      SizedBox(height: 8),
                      Text('For MS SQL Server:'),
                      Text('• Default port: 1433'),
                      Text('• Example: localhost:1433'),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _saveAndProceed() {
    if (_formKey.currentState!.validate()) {
      final vannaService = VannaService(
        apiKey: widget.apiKey,
        databaseType: _databaseTypeController.text,
        databaseUrl: _databaseUrlController.text,
        databaseUsername: _databaseUsernameController.text,
        databasePassword: _databasePasswordController.text,
        databaseName: _databaseNameController.text,
      );

      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => SQLGeneratorScreen(vannaService: vannaService),
        ),
      );
    }
  }

  @override
  void dispose() {
    _databaseTypeController.dispose();
    _databaseUrlController.dispose();
    _databaseUsernameController.dispose();
    _databasePasswordController.dispose();
    _databaseNameController.dispose();
    super.dispose();
  }
} 