# app/services/gpt_service.py

import os
import httpx
from openai import OpenAI
from dotenv import load_dotenv
from app.services.schema_service import SchemaService
from app.services.prompt_builder import build_prompt

load_dotenv()

MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "openai").lower()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def call_openai(question: str) -> str:
    schema_str = await SchemaService.get_full_schema_string()
    prompt = build_prompt(user_question=question, schema=schema_str)
    
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

        # Clean markdown formatting if present
        if "```sql" in sql:
            sql = sql.split("```sql")[1].split("```", 1)[0].strip()
        elif "```" in sql:
            sql = sql.split("```", 1)[1].split("```", 1)[0].strip()

        # Remove leading 'SQL:' if present
        sql = sql[4:].strip() if sql.lower().startswith("sql:") else sql

        return sql
    except Exception as e:
        raise RuntimeError(f"OpenAI error: {e}")


async def call_deepseek(question: str) -> str:
    schema_str = await SchemaService.get_full_schema_string()
    prompt = build_prompt(user_question=question, schema=schema_str)

    api_url = os.getenv("DEESEEK_API_URL", "http://localhost:11434/api/generate")

    payload = {
        "model": "deepseek-coder",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
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
                raw_sql = raw_sql.split("```sql")[1].split("```", 1)[0].strip()

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
