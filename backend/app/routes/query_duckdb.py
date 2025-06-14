# app/routes/query_duckdb.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.duckdb_instance import duckdb_instance
from app.services.duckdb_gpt_service import generate_sql_from_question

router = APIRouter()

class DuckDBQueryRequest(BaseModel):
    question: str
    table_name: str

class DuckDBQueryResponse(BaseModel):
    columns: list[str]
    rows: list[list]

@router.post("/duckdb-query/", response_model=DuckDBQueryResponse)
async def query_duckdb_endpoint(request: DuckDBQueryRequest):
    try:
        sql_query = await generate_sql_from_question(request.question, request.table_name, duckdb_instance)
        result = duckdb_instance.query(sql_query)
        return result

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DuckDB query error: {str(e)}")
