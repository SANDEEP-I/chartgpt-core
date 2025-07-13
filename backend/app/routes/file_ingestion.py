# app/routes/file_ingestion.py

from fastapi import APIRouter, UploadFile, HTTPException
from app.services.file_parser import FileParser
from app.services.duckdb_instance import duckdb_instance
import uuid
import logging

router = APIRouter()

@router.post("/upload/")
async def upload_file(file: UploadFile):
    try:
        # Save file locally
        file_path = FileParser.save_temp_file(file)

        # Parse file to validate
        file_type, df = FileParser.parse_file(file_path)

        # Generate unique table name
        unique_table_name = f"upload_{uuid.uuid4().hex[:8]}"

        # ✅ Ingest into DuckDB (shared instance used across query routes)
        duckdb_instance.conn.register("temp_df", df)
        duckdb_instance.conn.execute(f"CREATE TABLE {unique_table_name} AS SELECT * FROM temp_df")
        duckdb_instance.conn.unregister("temp_df")

        # ✅ Schema extraction
        schema = duckdb_instance.get_table_schema(unique_table_name)

        logging.info(f"[UPLOAD] Ingested '{file.filename}' as table '{unique_table_name}'")

        return {
            "message": "File ingested successfully",
            "table_name": unique_table_name,
            "schema": schema
        }

    except Exception as e:
        logging.error(f"[UPLOAD ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))
