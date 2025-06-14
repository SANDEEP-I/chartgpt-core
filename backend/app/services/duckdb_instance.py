# app/services/duckdb_instance.py

from app.services.duckdb_engine import DuckDBEngine

# Create one global DuckDB instance for the entire app
duckdb_instance = DuckDBEngine()
