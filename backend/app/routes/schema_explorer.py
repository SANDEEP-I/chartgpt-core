# app/routes/schema_explorer.py

from fastapi import APIRouter, HTTPException
from app.services.duckdb_instance import duckdb_instance

router = APIRouter()

@router.get("/schema-explorer/")
async def list_all_tables():
    try:
        tables = duckdb_instance.list_tables()
        response = []

        for table_name in tables:
            schema = duckdb_instance.get_table_schema(table_name)
            response.append({
                "table_name": table_name,
                "columns": schema
            })

        return {"tables": response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))