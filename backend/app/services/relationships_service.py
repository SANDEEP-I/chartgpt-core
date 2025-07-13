# app/services/relationships_service.py

import os
import asyncio
import psycopg2
import duckdb
import logging
from dotenv import load_dotenv
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

# ✅ Load environment variables
load_dotenv()

# ✅ PostgreSQL config
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

# ✅ Final fix: use parent of `services/` = `app/`, then go to `temp_uploads`
UPLOAD_DIR = Path(__file__).resolve().parents[2] / "temp_uploads"



class RelationshipsService:
    """
    Extracts foreign key relationships dynamically from PostgreSQL.
    Used for join orchestration layer.
    """

    @staticmethod
    def _fetch_relationships() -> List[tuple]:
        query = """
            SELECT
                tc.table_name AS source_table,
                kcu.column_name AS source_column,
                ccu.table_name AS target_table,
                ccu.column_name AS target_column
            FROM 
                information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                 AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                 AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_schema = 'public'
            ORDER BY source_table;
        """
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                return cur.fetchall()

    @classmethod
    async def get_relationships(cls) -> Dict[str, List[Dict[str, str]]]:
        loop = asyncio.get_running_loop()
        rows = await loop.run_in_executor(None, cls._fetch_relationships)

        relations: Dict[str, List[Dict[str, str]]] = {}
        for source_table, source_column, target_table, target_column in rows:
            key = source_table.lower()
            if key not in relations:
                relations[key] = []
            relations[key].append({
                "source_column": source_column,
                "target_table": target_table,
                "target_column": target_column
            })
        return relations


# ✅ DuckDB-based FK inference from uploaded CSVs
async def extract_foreign_keys() -> List[Dict]:
    """
    Infer foreign key relationships between uploaded DuckDB tables based on column name matching.
    Includes absolute path resolution and debug logging.
    """
    conn = duckdb.connect(database=":memory:")
    table_columns = {}

    logging.info("[RELATIONSHIP INFERRER] Starting FK inference...")

    if not UPLOAD_DIR.exists():
        logging.error(f"[ERROR] Upload directory does not exist: {UPLOAD_DIR}")
        return []

    # Step 1: Log all files
    logging.info("[DEBUG] Listing ALL files in temp_uploads:")
    for f in UPLOAD_DIR.iterdir():
        logging.info(f" - Found: {f.name}")

    # Step 2: Collect CSV files
    csv_files = list(UPLOAD_DIR.glob("*.csv"))
    logging.info(f"[DEBUG] Found {len(csv_files)} CSV files matching '*.csv'")

    for file in csv_files:
        table = file.stem.lower()
        abs_path = file.resolve()
        logging.info(f"[LOAD] Ingesting file: '{file.name}' as table: '{table}'")
        logging.info(f"[PATH] Absolute path used: {abs_path}")

        try:
            conn.execute(f"""
                CREATE OR REPLACE TABLE {table} AS
                SELECT * FROM read_csv_auto('{abs_path}', HEADER=TRUE);
            """)
            # ✅ FIXED: use col[1] for column name
            cols = [col[1].lower() for col in conn.execute(f"PRAGMA table_info('{table}')").fetchall()]
            logging.info(f"[SCHEMA] Columns in '{table}': {cols}")
            table_columns[table] = cols
        except Exception as e:
            logging.error(f"[ERROR] Failed to load '{file.name}': {e}")

    # Step 3: Column-to-table mapping
    column_to_tables = defaultdict(list)
    for table, columns in table_columns.items():
        for col in columns:
            column_to_tables[col].append(table)

    logging.info(f"[MAPPING] Column-to-table map: {dict(column_to_tables)}")

    # Step 4: Inference
    relationships = []
    for col, tables in column_to_tables.items():
        if len(tables) <= 1:
            continue

        for source in tables:
            for target in tables:
                if source == target:
                    continue

                relation = {
                    "source_table": source,
                    "source_column": col,
                    "target_table": target,
                    "target_column": col,
                    "confidence": 0.9,
                    "fk_type": "many-to-one",
                    "inferred_by": "column_name_match",
                    "is_user_verified": False
                }

                logging.info(f"[RELATIONSHIP] {relation}")
                relationships.append(relation)

    logging.info(f"[DONE] Total relationships inferred: {len(relationships)}")
    return relationships
