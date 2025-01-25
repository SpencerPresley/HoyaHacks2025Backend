from __future__ import annotations

import os
from typing import Optional, TYPE_CHECKING, List, Dict, Union
from enum import Enum

if TYPE_CHECKING:
    from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

class ResumeSection(Enum):
    BASIC_INFO = "basic_info"
    OBJECTIVE = "objective"
    EDUCATION = "education"
    EXPERIENCE = "experience"
    SKILLS = "skills"
    PROJECTS = "projects"

class VectorDBSearcher:
    def __init__(
        self, 
        vector_db_dir: Path, 
        database_name: str, 
        embeddings: OpenAIEmbeddings
    ):
        self.vector_db_dir = vector_db_dir
        self.database_name = database_name
        self.embeddings = embeddings

        # Enhanced metadata schema for resumes
        self.metadata_schema = {
            "section": [section.value for section in ResumeSection],
            "source": [],  # Will be populated with resume filenames
            "name": [],    # Will be populated with candidate names
            "email": [],   # Will be populated with candidate emails
        }
        self.database = self.load_database()

    def load_database(self) -> FAISS:
        """Load the FAISS database and attach metadata schema."""
        try:
            db = FAISS.load_local(
                self.vector_db_dir,
                self.embeddings,
                self.database_name,
                allow_dangerous_deserialization=True,
            )
            # Attach metadata schema to loaded database
            db.metadata_schema = self.metadata_schema
            return db
        except Exception as e:
            raise RuntimeError(f"Failed to load database: {e}")

    def get_relevant_candidates(
        self,
        prompt: str,
        *,
        section: Optional[Union[ResumeSection, str]] = None, # filter by section
        source_file: Optional[str] = None, # filter by source file
        candidate_name: Optional[str] = None, # filter by candidate name
        candidate_email: Optional[str] = None, # filter by candidate email
        max_docs: int = 5, # number of candidates to return
        score_threshold: float = 0.5, # minimum relevance score
    ) -> List[Dict]:
        """Enhanced search with multiple filtering options.

        Args:
            prompt: Search query
            section: Specific resume section to search in
            source_file: Specific resume file to search in
            candidate_name: Search by candidate name
            candidate_email: Search by candidate email
            max_docs: Maximum number of documents to return
            score_threshold: Minimum relevance score (0-1)

        Returns:
            List[Dict]: List of relevant documents with their metadata
        """
        try:
            metadata_filter = {}

            # Add section filter if specified
            if section:
                section_value = section.value if isinstance(section, ResumeSection) else section
                metadata_filter["section"] = section_value

            # Add other filters if specified
            if source_file:
                metadata_filter["source"] = source_file
            if candidate_name:
                metadata_filter["name"] = candidate_name
            if candidate_email:
                metadata_filter["email"] = candidate_email

            # Perform search with filters
            docs_and_scores = self.database.similarity_search_with_relevance_scores(
                prompt,
                k=max_docs,
                filter=metadata_filter if metadata_filter else None
            )

            # Format results with metadata
            results = []
            for doc, score in docs_and_scores:
                if score >= score_threshold:
                    results.append({
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "relevance_score": score
                    })

            return results[:max_docs]

        except Exception as e:
            print(f"Warning: Failed to retrieve relevant documents: {e}")
            return []

    def search_by_section(
        self,
        section: ResumeSection, # specifically get candidates from this section
        prompt: str,
        max_docs: int = 3
    ) -> List[Dict]:
        """Convenience method to search within a specific section"""
        return self.get_relevant_docs(
            prompt=prompt,
            section=section,
            max_docs=max_docs
        )

    def search_by_candidate( # search by candidate name or email
        self,
        prompt: str,
        *,
        name: Optional[str] = None,
        email: Optional[str] = None,
        max_docs: int = 3
    ) -> List[Dict]:
        """Convenience method to search by candidate info"""
        return self.get_relevant_docs(
            prompt=prompt,
            candidate_name=name,
            candidate_email=email,
            max_docs=max_docs
        )