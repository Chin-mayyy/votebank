class SQLResponse {
  final String sql;
  final String? error;
  final bool isLoading;

  SQLResponse({
    required this.sql,
    this.error,
    this.isLoading = false,
  });

  SQLResponse copyWith({
    String? sql,
    String? error,
    bool? isLoading,
  }) {
    return SQLResponse(
      sql: sql ?? this.sql,
      error: error ?? this.error,
      isLoading: isLoading ?? this.isLoading,
    );
  }
} 