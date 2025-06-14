# app/services/duckdb_engine.py

import duckdb
from typing import List, Dict, Any

class DuckDBEngine:
    """
    Core DuckDB Engine to load files in-memory and expose SQL querying interface.
    """

    def __init__(self):
        # In-memory DuckDB instance
        self.conn = duckdb.connect(database=':memory:')

    def register_csv(self, table_name: str, file_path: str, header: bool = True):
        """
        Register CSV file as a virtual table in DuckDB.
        """
        self.conn.execute(f"""
            CREATE OR REPLACE TABLE {table_name} AS 
            SELECT * FROM read_csv_auto('{file_path}', HEADER={str(header).upper()});
        """)

    def register_parquet(self, table_name: str, file_path: str):
        """
        Register Parquet file as virtual table.
        """
        self.conn.execute(f"""
            CREATE OR REPLACE TABLE {table_name} AS 
            SELECT * FROM read_parquet('{file_path}');
        """)

    def get_table_schema(self, table_name: str) -> Dict[str, str]:
        """
        Extract column names and data types for GPT prompt injection.
        """
        result = self.conn.execute(f"PRAGMA table_info({table_name});").fetchall()
        return {row[1]: row[2] for row in result}

    def query(self, sql: str) -> Dict[str, Any]:
        """
        Execute SQL query and return results in frontend-friendly format.
        """
        result = self.conn.execute(sql)
        columns = [desc[0] for desc in result.description]
        rows = result.fetchall()
        return {"columns": columns, "rows": rows}

    def list_tables(self) -> List[str]:
        """
        List all registered tables in DuckDB.
        """
        result = self.conn.execute("SHOW TABLES;").fetchall()
        return [row[0] for row in result]

    def drop_table(self, table_name: str):
        """
        Drop table from DuckDB memory.
        """
        self.conn.execute(f"DROP TABLE IF EXISTS {table_name};")
