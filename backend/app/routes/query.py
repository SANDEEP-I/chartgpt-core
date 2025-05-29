# ✅ app/routes/query.py

import re
from sqlparse import split
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.gpt_service import generate_sql_from_question
from app.services.db_service import run_sql_query, validate_sql_columns
from app.services.response_formatter import format_response_for_frontend


router = APIRouter()

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    columns: list[str]
    rows: list[list]

@router.post("/")
async def query_endpoint(request: QueryRequest):
    try:
        sql_query = await generate_sql_from_question(request.question)

        # 🛡️ Block write operations
        if re.search(r"\b(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b", sql_query, re.IGNORECASE):
            raise HTTPException(400, detail="Only read-only SELECT queries are allowed.")

        # 🧼 Fix malformed FROM clause
        sql_query = re.sub(r'(\S)(?=\bfrom\b)', r'\1 ', sql_query, flags=re.IGNORECASE)

        # 🧼 Comment-only fallback
        if sql_query.strip().startswith("/*"):
            return {
                "columns": ["Error"],
                "rows": [[sql_query.strip()]]
            }

        await validate_sql_columns(sql_query)

        # 🔒 Sanitize multi-statement SQL
        sql_query = sql_query.split(";")[0].strip()
        raw_result = await run_sql_query(sql_query)
        return format_response_for_frontend(raw_result["columns"], raw_result["rows"])


    except ValueError as ve:
        raise HTTPException(400, detail=str(ve))
    except Exception as e:
        raise HTTPException(500, detail=f"Server error: {str(e)}")
