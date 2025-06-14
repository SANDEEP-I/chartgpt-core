# app/services/relationships_service.py

import os
import psycopg2
import asyncio
from dotenv import load_dotenv
from typing import Dict, List

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

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
