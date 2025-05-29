# ✅ app/services/gpt_service.py

import os
import httpx
from openai import OpenAI
from dotenv import load_dotenv
from app.services.db_service import get_database_schema, table_info
from app.services.prompt_builder import build_prompt

load_dotenv()

MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "openai").lower()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SQL_PROMPT_TEMPLATE = """
You are a data analyst. Convert the following natural language question into a SQL query.

Only use this table:

orders(customer_name, product_name, quantity, price, order_date, region)

This is a PostgreSQL database — not MySQL or SQL Server.

✅ Use these functions:
- DATE_TRUNC('month', order_date) → to group by month
- EXTRACT(YEAR FROM order_date) = 2024 → to filter by year

DO NOT use `MONTH()` or compare years using subtraction.

Question: "{question}"

SQL:
"""

async def call_openai(question: str) -> str:
    prompt = SQL_PROMPT_TEMPLATE.format(question=question)
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

        # 🧼 Remove markdown block if present
        if "```sql" in sql:
            sql = sql.split("```sql")[1].split("```")[0].strip()
        elif "```" in sql:
            sql = sql.split("```")[1].split("```")[0].strip()

        # 🧹 Remove leading "SQL:" label if present
        sql = sql[4:].strip() if sql.lower().startswith("sql:") else sql

        return sql
    except Exception as e:
        raise RuntimeError(f"OpenAI error: {e}")


async def call_deepseek(question: str) -> str:
    schema_str = await get_database_schema()
    formatted_schema = table_info(schema_str)

    prompt = f'''
### Critical Formatting Rules
1. NEVER use table prefixes (e.g., use "customer_name" NOT "orders.customer_name")
2. If ANY requested columns are missing, respond with EXACTLY:
   /* Error: Missing columns. Available: id, customer_name, product_name, quantity, price, order_date, region */
3. Never include JOIN clauses
4. Use only these date functions: EXTRACT(), DATE_TRUNC()
5. Always put a space between column list and FROM
6. Use explicit comma separation

### BAD Example:
SELECT customer_name,product_nameFROM orders;

### GOOD Example:
SELECT customer_name, product_name FROM orders;

### Schema
{formatted_schema}

### Question
{question}

SQL:
'''.strip()

    api_url = os.getenv("DEESEEK_API_URL", "http://localhost:11434/api/generate")

    payload = {
        "model": "deepseek-coder",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,  # Lowered for stricter behavior
            "num_predict": 200,
            "repeat_penalty": 1.5
        }
    }

    try:
        timeout = httpx.Timeout(30.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(api_url, json=payload)
            response.raise_for_status()
            data = response.json()
            raw_sql = data.get("response", "").strip()

            if "```sql" in raw_sql:
                raw_sql = raw_sql.split("```sql")[1].split("```")[0].strip()

            return raw_sql
    except httpx.ReadTimeout:
        raise RuntimeError("DeepSeek API timeout - try again later")
    except Exception as e:
        raise RuntimeError(f"DeepSeek error: {e}")
    

async def generate_sql_from_question(question: str) -> str:
    if MODEL_PROVIDER == "openai":
        return await call_openai(question)
    elif MODEL_PROVIDER == "deepseek":
        return await call_deepseek(question)
    else:
        raise ValueError(f"Unsupported MODEL_PROVIDER: {MODEL_PROVIDER}")

    

    