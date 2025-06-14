# app/services/schema_service.py

import os
import psycopg2
import asyncio
from dotenv import load_dotenv
from typing import Dict, List, Any
from app.services.relationships_service import RelationshipsService

# Load environment variables
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

class SchemaService:
    """
    Schema extraction service - provides full database schema dynamically.
    Fully future-proof for multi-table, joins, keys, and GPT schema injection.
    """

    @staticmethod
    def _fetch_schema() -> List[Dict[str, Any]]:
        query = """
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position;
        """
        
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()
                return rows

    @classmethod
    async def get_schema_dict(cls) -> Dict[str, List[Dict[str, str]]]:
        loop = asyncio.get_running_loop()
        rows = await loop.run_in_executor(None, cls._fetch_schema)

        schema: Dict[str, List[Dict[str, str]]] = {}
        for table, column, data_type in rows:
            table = table.lower()
            if table not in schema:
                schema[table] = []
            schema[table].append({"column": column.lower(), "type": data_type})
        return schema

    @classmethod
    async def get_relationships(cls) -> Dict[str, List[Dict[str, str]]]:
        return await RelationshipsService.get_relationships()

    @classmethod
    async def get_full_schema_string(cls) -> str:
        schema_dict = await cls.get_schema_dict()
        relationships = await cls.get_relationships()

        parts = []
        for table, columns in schema_dict.items():
            cols = ", ".join([col["column"] for col in columns])
            parts.append(f"{table}({cols})")
        
        parts.append("\nRelationships:")
        
        for source_table, rels in relationships.items():
            for rel in rels:
                parts.append(f"{source_table}.{rel['source_column']} → {rel['target_table']}.{rel['target_column']}")

        return "\n".join(parts)

    @classmethod
    async def get_column_set(cls) -> List[str]:
        schema_dict = await cls.get_schema_dict()
        column_set = set()
        for columns in schema_dict.values():
            for col in columns:
                column_set.add(col["column"])
        return sorted(column_set)
