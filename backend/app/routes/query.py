# app/routes/query.py

import re
from sqlparse import split
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.gpt_service import generate_sql_from_question
from app.services.db_service import run_sql_query, validate_sql_columns

router = APIRouter()

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    columns: list[str]
    rows: list[list]

@router.post("/", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    try:
        # Step 1 — Generate SQL via GPT
        sql_query = await generate_sql_from_question(request.question)

        # Step 2 — Guard: allow only read-only queries
        if re.search(r"\b(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE)\b", sql_query, re.IGNORECASE):
            raise HTTPException(400, detail="Only read-only SELECT queries are allowed.")

        # Step 3 — Clean malformed FROM clause (GPT sometimes messes formatting)
        sql_query = re.sub(r'(\S)(?=\bfrom\b)', r'\1 ', sql_query, flags=re.IGNORECASE)

        # Step 4 — Handle GPT fallback comment response
        if sql_query.strip().startswith("/*"):
            return {
                "columns": ["Error"],
                "rows": [[sql_query.strip()]]
            }

        # Step 5 — Validate columns dynamically via SchemaService
        await validate_sql_columns(sql_query)

        # Step 6 — Sanitize multi-statement SQL: only execute first statement
        sql_query = sql_query.split(";")[0].strip()

        # Step 7 — Run the query
        result = await run_sql_query(sql_query)
        return result

    except ValueError as ve:
        raise HTTPException(400, detail=str(ve))
    except Exception as e:
        raise HTTPException(500, detail=f"Server error: {str(e)}")
