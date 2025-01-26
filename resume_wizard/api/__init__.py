import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_openai import OpenAIEmbeddings

from resume_wizard.vectordb.searcher import VectorDBSearcher
from resume_wizard.vectordb.manager import VECTOR_DB_DIR, VECTOR_DB_NAME
from .dependencies import set_searcher
from .routes import router

load_dotenv()

app = FastAPI(title="Resume Search API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your Next.js frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize VectorDBSearcher with the same paths used in the manager
openai_api_key = os.getenv("OPENAI_API_KEY")
embeddings = OpenAIEmbeddings(api_key=openai_api_key)

# Use the same path from manager
searcher = VectorDBSearcher(VECTOR_DB_DIR, VECTOR_DB_NAME, embeddings)

# Set the global searcher instance
set_searcher(searcher)

# Include router
app.include_router(
    router,
    prefix="/api",
    tags=["search"]
)
