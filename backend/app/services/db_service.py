# ✅ app/services/db_service.py

import os
import psycopg2
import asyncio
import sqlparse
from dotenv import load_dotenv
from typing import Set
import re


# Load .env variables
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

def _execute_query(sql: str):
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            return {"columns": columns, "rows": rows}

async def run_sql_query(sql: str) -> dict:
    loop = asyncio.get_running_loop()
    try:
        result = await loop.run_in_executor(None, _execute_query, sql)
        return result
    except Exception as e:
        raise RuntimeError(f"Database query failed: {e}")

async def get_database_schema() -> str:
    query = """
        SELECT table_name, column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position;
    """

    loop = asyncio.get_running_loop()
    def _fetch():
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                return cur.fetchall()

    rows = await loop.run_in_executor(None, _fetch)
    schema = {}
    for table, column in rows:
        schema.setdefault(table.lower(), []).append(column.lower())

    formatted = "\n".join(f"{table}({', '.join(columns)})" for table, columns in schema.items())
    return formatted

def table_info(schema_str: str) -> str:
    schema = {}
    for line in schema_str.strip().splitlines():
        if '(' not in line or ')' not in line:
            continue
        table, cols = line.split("(", 1)
        table = table.strip().lower()
        columns = [col.strip().lower() for col in cols.rstrip(")").split(",")]
        schema[table] = columns
    return "\n".join(f"{table}({', '.join(columns)})" for table, columns in schema.items())

async def validate_sql_columns(sql: str) -> bool:
    schema_str = await get_database_schema()

    valid_columns = set()
    table_columns = {}
    for line in schema_str.strip().splitlines():
        if '(' not in line:
            continue
        table, cols = line.split("(", 1)
        table = table.strip().lower()
        columns = [col.strip().lower() for col in cols.rstrip(")").split(",")]
        table_columns[table] = set(columns)
        valid_columns.update(columns)

    sql = sql.replace("(", " ").replace(")", " ")
    parsed = sqlparse.parse(sql.lower())[0]

    columns_used = set()

    select_tokens = []
    in_select = False
    for token in parsed.tokens:
        if isinstance(token, sqlparse.sql.Token) and token.value.startswith('select'):
            in_select = True
            continue
        if in_select and token.value.lower().startswith('from'):
            break
        if in_select:
            select_tokens.extend(token.flatten())

    for token in select_tokens:
        if isinstance(token, sqlparse.sql.Identifier):
            raw_value = token.value.replace("(", " ").replace(")", " ")
            for part in re.split(r'[+*/\\-]', raw_value):  # split on arithmetic operators
                subparts = re.findall(r'\\b([a-z_][a-z0-9_]*)\\b', part.lower())
                columns_used.update(subparts)

    invalid_cols = [col for col in columns_used if col not in valid_columns]
    if invalid_cols:
        raise ValueError(
            f"Invalid columns ({', '.join(invalid_cols)}). Available: {', '.join(valid_columns)}"
        )

    return True