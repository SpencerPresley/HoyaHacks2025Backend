from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Set

from resume_wizard.vectordb.searcher import VectorDBSearcher, ResumeSection
from .dependencies import get_searcher

router = APIRouter()

class SearchQuery(BaseModel):
    query: str
    section: Optional[str] = None
    max_results: Optional[int] = 5
    score_threshold: Optional[float] = 0.5

class SearchResult(BaseModel):
    source: str
    score: float
    content: str
    section: str

@router.post("/search", response_model=List[SearchResult])
async def search_resumes(
    search_query: SearchQuery,
    searcher: VectorDBSearcher = Depends(get_searcher)
):
    """Search through resumes using vector similarity search.
    
    Args:
        search_query: The search parameters
        searcher: VectorDBSearcher instance (injected via dependency)
        
    Returns:
        List[SearchResult]: List of matching resume sections with their sources
    """
    try:
        results = searcher.get_relevant_candidates(
            prompt=search_query.query,
            section=search_query.section,
            max_docs=search_query.max_results,
            score_threshold=search_query.score_threshold
        )
        
        return [
            SearchResult(
                source=result["metadata"]["source"],
                score=result["relevance_score"],
                content=result["content"],
                section=result["metadata"]["section"]
            )
            for result in results
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching resumes: {str(e)}"
        )

@router.post("/search/sources")
async def search_resume_sources(
    search_query: SearchQuery,
    searcher: VectorDBSearcher = Depends(get_searcher)
) -> List[str]:
    try:
        results = searcher.get_relevant_candidates(
            prompt=search_query.query,
            section=search_query.section,
            max_docs=search_query.max_results,
            score_threshold=search_query.score_threshold
        )
        # Extract unique source files using a set
        sources = {result["metadata"]["source"] for result in results}
        return list(sources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
