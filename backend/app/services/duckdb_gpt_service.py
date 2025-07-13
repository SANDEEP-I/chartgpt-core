# app/services/duckdb_gpt_service.py

import os
import logging
from openai import OpenAI
from dotenv import load_dotenv
from app.services.duckdb_engine import DuckDBEngine

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def build_multi_table_prompt(user_question: str, all_schemas: dict) -> str:
    """
    Build a GPT prompt with schemas of all tables.
    """
    schema_parts = []
    for table, schema in all_schemas.items():
        columns = [f"{col} ({dtype})" for col, dtype in schema.items()]
        schema_parts.append(f"Table: {table}\n" + "\n".join(columns))

    schema_str = "\n\n".join(schema_parts)

    prompt = f"""
You are a SQL generator. Write a PostgreSQL-compliant SQL query based on the user's question and the provided table schemas.

{schema_str}

Rules:
- Use only columns from the listed schemas.
- Do not use table prefixes or aliases.
- Do not use markdown formatting.
- Generate only the SQL query (no explanations).

Question: {user_question}
SQL:
"""
    return prompt.strip()

async def generate_sql_from_question(question: str, _ignored_table: str, duckdb_instance: DuckDBEngine) -> str:
    """
    Generate SQL using all uploaded tables' schemas.
    `_ignored_table` is ignored but kept for backward compatibility with the route signature.
    """
    try:
        all_tables = duckdb_instance.list_tables()
        if not all_tables:
            raise ValueError("No tables found in DuckDB instance.")

        all_schemas = {table: duckdb_instance.get_table_schema(table) for table in all_tables}
        prompt = build_multi_table_prompt(question, all_schemas)

        logging.info(f"[GPT PROMPT]\n{prompt}")

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that writes SQL for PostgreSQL."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
        )

        sql = response.choices[0].message.content.strip()

        # Strip markdown/code block wrappers
        if "```sql" in sql:
            sql = sql.split("```sql")[1].split("```", 1)[0].strip()
        elif "```" in sql:
            sql = sql.split("```", 1)[1].split("```", 1)[0].strip()

        sql = sql[4:].strip() if sql.lower().startswith("sql:") else sql

        logging.info(f"[SQL GENERATED]\n{sql}")
        return sql

    except Exception as e:
        logging.error(f"[OpenAI ERROR] {e}")
        raise RuntimeError(f"OpenAI error: {e}")
