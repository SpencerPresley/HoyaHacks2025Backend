import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from langchain_openai import OpenAIEmbeddings

from resume_wizard.vectordb.searcher import VectorDBSearcher
from resume_wizard.vectordb.manager import VECTOR_DB_DIR, VECTOR_DB_NAME
from .dependencies import set_searcher
from .routes import router

load_dotenv()

app = FastAPI(title="Resume Search API")

# Initialize VectorDBSearcher with the same paths used in the manager
openai_api_key = os.getenv("OPENAI_API_KEY")
embeddings = OpenAIEmbeddings(api_key=openai_api_key)

# Prepend resume_wizard to the path
vector_db_path = Path("resume_wizard") / VECTOR_DB_DIR
searcher = VectorDBSearcher(vector_db_path, VECTOR_DB_NAME, embeddings)

# Set the global searcher instance
set_searcher(searcher)

# Include router
app.include_router(
    router,
    prefix="/api",
    tags=["search"]
)
