# app/services/duckdb_gpt_service.py

import os
from openai import OpenAI
from dotenv import load_dotenv
from app.services.duckdb_engine import DuckDBEngine

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def build_prompt(user_question: str, table_name: str, schema: dict) -> str:
    schema_lines = [f"{col} ({dtype})" for col, dtype in schema.items()]
    schema_str = f"Table: {table_name}\n" + "\n".join(schema_lines)

    prompt = f"""
You are a SQL generator. Write a PostgreSQL-compliant SQL query based on user's question.

{schema_str}

Rules:
- Only use columns from the schema.
- No table prefixes.
- Do not use aliases (AS).
- Always assume correct column names.
- Do not include markdown.

Question: {user_question}
SQL:
"""
    return prompt

async def generate_sql_from_question(question: str, table_name: str, duckdb_instance: DuckDBEngine) -> str:
    schema = duckdb_instance.get_table_schema(table_name)
    prompt = build_prompt(question, table_name, schema)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that writes SQL for PostgreSQL."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
        )
        sql = response.choices[0].message.content.strip()

        # Clean up markdown if returned
        if "```sql" in sql:
            sql = sql.split("```sql")[1].split("```", 1)[0].strip()
        elif "```" in sql:
            sql = sql.split("```", 1)[1].split("```", 1)[0].strip()

        sql = sql[4:].strip() if sql.lower().startswith("sql:") else sql
        return sql
    except Exception as e:
        raise RuntimeError(f"OpenAI error: {e}")
