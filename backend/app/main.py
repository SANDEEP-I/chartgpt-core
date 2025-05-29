# FastAPI entry point
# app/main.py

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

# Set up CORS middleware to allow all origins (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # In production, replace with specific allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include the /query route
from app.routes.query import router as query_router
app.include_router(query_router, prefix="/query")

# Root route to verify the API is running
@app.get("/")
async def root():
    return {"message": "ChartGPT API is running"}
