import 'package:flutter/material.dart';
import 'dart:async';
import 'screens/home_screen.dart';
import 'dart:developer' as developer;

void main() {
  runZonedGuarded(() {
    WidgetsFlutterBinding.ensureInitialized();
    FlutterError.onError = (FlutterErrorDetails details) {
      developer.log('Flutter error: ${details.exception}',
          error: details.exception, stackTrace: details.stack);
    };
    
    runApp(const VoteBankApp());
  }, (error, stack) {
    developer.log('Uncaught error:', error: error, stackTrace: stack);
  });
}

class VoteBankApp extends StatelessWidget {
  const VoteBankApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'VoteBank Q&A',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}
