# app/services/db_service.py

import os
import psycopg2
import asyncio
import sqlparse
import re
from dotenv import load_dotenv
from app.services.schema_service import SchemaService

# Load environment variables
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

# -------------------
# SQL Execution
# -------------------

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

# -------------------
# Column Validation
# -------------------

async def validate_sql_columns(sql: str) -> bool:
    schema_dict = await SchemaService.get_schema_dict()

    # Build full valid column set
    valid_columns = set()
    for columns in schema_dict.values():
        valid_columns.update(col["column"] for col in columns)

    # Normalize SQL for token parsing
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
            for part in re.split(r'[+*/\\-]', raw_value):
                subparts = re.findall(r'\\b([a-z_][a-z0-9_]*)\\b', part.lower())
                columns_used.update(subparts)

    # Compare used columns with valid columns
    invalid_cols = [col for col in columns_used if col not in valid_columns]
    if invalid_cols:
        raise ValueError(
            f"Invalid columns ({', '.join(invalid_cols)}). Available: {', '.join(valid_columns)}"
        )

    return True
