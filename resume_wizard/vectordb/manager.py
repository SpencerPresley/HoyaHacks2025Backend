import os
import json
from dotenv import load_dotenv
from typing import Dict, Any, List
from pathlib import Path

from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS

from resume_wizard.globals import RESUMES_DIR
from resume_wizard.wizard import run_resume_wizard

# Add vector db directory constant
VECTOR_DB_DIR = Path("vectordb/vector_db")
VECTOR_DB_NAME = "resume_db"

load_dotenv()

class VectorDBManager:
    def __init__(
        self,
        api_key: str,
        index_type: str | None = "HNSW"
    ):
        self._embeddings = OpenAIEmbeddings(api_key=api_key)
        self._embedding_size = len(self._embeddings.embed_query("test"))
        self._index = self._create_index(index_type)
        self._raw_data = self._get_raw_resume_data()
        self.db = None
        
        # Create vector db directory if it doesn't exist
        VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
        
    def create_db(self) -> FAISS:
        try:
            self.db = FAISS(
                embedding_function=self._embeddings,
                index=self._index,
                docstore=InMemoryDocstore(),
                index_to_docstore_id={}
            )
            return self
        except Exception as e:
            print(f"Error creating FAISS database: {e}")
            return None
        
    def add_docs_to_db(self) -> None:
        if not self.db:
            raise ValueError("Database not created. Call create_db() first.")
        
        for pdf_file, resume_data in zip(os.listdir(RESUMES_DIR), self._raw_data):
            documents = self._process_resume_data(resume_data, pdf_file)
            self.db.add_documents(documents)
        
        return self
    
    def get_db(self) -> FAISS:
        return self.db
        
    def _create_index(self, index_type: str) -> faiss.Index:
        if index_type == "HNSW":
            try:
                return faiss.IndexHNSWFlat(self._embedding_size, 32)
            except Exception as e:
                print(f"Error creating HNSW index: {e}")
                return faiss.IndexFlatL2(self._embedding_size)
        else:
            try:
                return faiss.IndexFlatL2(self._embedding_size)
            except Exception as e:
                print(f"Error creating Flat index: {e}")
                return faiss.IndexFlatL2(self._embedding_size)
        
    def _get_raw_resume_data(self) -> list[dict]:
        resume_pdfs = os.listdir(RESUMES_DIR)
        data: list[dict] = []
        for pdf in resume_pdfs:
            resume_data = run_resume_wizard(pdf)
            data.append(resume_data)
        return data
        
    def _process_resume_data(self, resume_data: Dict[str, Any], pdf_file: str) -> List[Document]:
        """Process resume data into documents for vector storage.
        
        Args:
            resume_data: The parsed resume data
            pdf_file: The name of the PDF file
            
        Returns:
            List[Document]: List of documents ready for vector storage
        """
        documents = []
        
        # Convert skills dict to string representation
        skills_str = "Skills:\n"
        skills_data = resume_data.get("skills", {})
        for category, skills in skills_data.items():
            if skills:  # Only add category if it has skills
                skills_str += f"{category.title()}: {', '.join(skills)}\n"
        
        # Add skills document if we have skills
        if skills_str != "Skills:\n":
            documents.append(Document(
                page_content=skills_str,
                metadata={
                    "source": pdf_file,
                    "section": "skills"
                }
            ))
        
        # Add objective document if it exists
        objective = resume_data.get("objective")
        if objective:
            documents.append(Document(
                page_content=str(objective),
                metadata={
                    "source": pdf_file,
                    "section": "objective"
                }
            ))
        
        # Add experience documents
        for exp in resume_data.get("experience", []):
            if exp.get("position") and exp.get("company"):
                content = f"{exp.get('position')} at {exp.get('company')}"
                if exp.get("description"):
                    content += f"\n{exp.get('description')}"
                    
                documents.append(Document(
                    page_content=content,
                    metadata={
                        "source": pdf_file,
                        "section": "experience",
                        "position": exp.get("position"),
                        "company": exp.get("company")
                    }
                ))
        
        # Add project documents
        for proj in resume_data.get("projects", []):
            if proj.get("name"):
                content = proj.get("name", "")
                if proj.get("description"):
                    content += f"\n{proj.get('description')}"
                    
                documents.append(Document(
                    page_content=content,
                    metadata={
                        "source": pdf_file,
                        "section": "projects",
                        "name": proj.get("name")
                    }
                ))
        
        return documents
    
if __name__ == "__main__":
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    vdb_manager = VectorDBManager(openai_api_key)
    vdb = vdb_manager.create_db().add_docs_to_db().get_db()
    vdb.save_local(str(VECTOR_DB_DIR), VECTOR_DB_NAME)
