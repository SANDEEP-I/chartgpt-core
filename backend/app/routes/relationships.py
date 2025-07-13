# app/routes/relationships.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.services.relationships_service import extract_foreign_keys
import logging

router = APIRouter()

class Relationship(BaseModel):
    source_table: str
    source_column: str
    target_table: str
    target_column: str
    confidence: float = 1.0  # Confidence score (0.0 - 1.0)
    fk_type: str = "many-to-one"  # e.g., "one-to-one", "many-to-one"
    inferred_by: str = "column_name_match"  # Inference method used
    is_user_verified: bool = False  # Has the user confirmed this FK?

@router.get("/", response_model=List[Relationship], tags=["Relationships"])
async def get_foreign_keys():
    """
    Return inferred foreign key relationships between uploaded DuckDB tables.
    """
    try:
        relationships = await extract_foreign_keys()
        return relationships
    except Exception as e:
        logging.exception("Error extracting foreign keys")
        raise HTTPException(status_code=500, detail=f"Relationship inference failed: {str(e)}")
