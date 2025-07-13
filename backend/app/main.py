# app/main.py

import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="ChartGPT API",
    description="Natural language to charts via GPT and SQL",
    version="1.0.0"
)

# Set up CORS middleware to allow frontend calls (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import all routes here
from app.routes.query import router as query_router
from app.routes.file_ingestion import router as file_ingestion_router
from app.routes.query_duckdb import router as query_duckdb_router
from app.routes.schema_explorer import router as schema_explorer_router
from app.routes.relationships import router as relationships_router  # ✅ NEW

# Include routers
app.include_router(query_router, prefix="/query")
app.include_router(file_ingestion_router)
app.include_router(query_duckdb_router)
app.include_router(schema_explorer_router)
app.include_router(relationships_router, prefix="/api/relationships")  # ✅ NEW

# Root health check route
@app.get("/")
async def root():
    return {"message": "ChartGPT API is running"}
