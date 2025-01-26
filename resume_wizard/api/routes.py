from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Set
import os
from pathlib import Path
import json

from resume_wizard.vectordb.searcher import VectorDBSearcher, ResumeSection
from resume_wizard.vectordb.manager import VectorDBManager
from resume_wizard.globals import RESUMES_DIR
from resume_wizard.wizard.rezwiz import run_resume_wizard
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

class CandidateSearchQuery(BaseModel):
    name: str
    max_results: Optional[int] = 5
    score_threshold: Optional[float] = 0.5

class FileSearchQuery(BaseModel):
    filename: str
    max_results: Optional[int] = 100
    score_threshold: Optional[float] = 0.5

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

@router.post("/search/candidate")
async def search_by_candidate_name(
    search_query: CandidateSearchQuery,
    searcher: VectorDBSearcher = Depends(get_searcher)
) -> List[SearchResult]:
    """Search for a specific candidate by name.
    
    Args:
        search_query: The search parameters including candidate name
        searcher: VectorDBSearcher instance (injected via dependency)
        
    Returns:
        List[SearchResult]: List of matching resume sections for that candidate
    """
    try:
        results = searcher.get_relevant_candidates(
            prompt="",  # Empty prompt since we're filtering by name
            candidate_name=search_query.name,
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
            detail=f"Error searching for candidate: {str(e)}"
        )

@router.post("/search/file")
async def search_by_filename(
    search_query: FileSearchQuery,
    searcher: VectorDBSearcher = Depends(get_searcher)
) -> List[SearchResult]:
    """Search for all sections from a specific resume file.
    
    Args:
        search_query: The search parameters including filename
        searcher: VectorDBSearcher instance (injected via dependency)
        
    Returns:
        List[SearchResult]: List of all sections from that resume
    """
    try:
        results = searcher.get_relevant_candidates(
            prompt="",  # Empty prompt since we're filtering by file
            source_file=search_query.filename,
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
            detail=f"Error searching by filename: {str(e)}"
        )

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    searcher: VectorDBSearcher = Depends(get_searcher)
) -> dict:
    """Upload a resume and add it to the vector database.
    
    Args:
        file: The uploaded PDF file
        searcher: VectorDBSearcher instance (injected via dependency)
        
    Returns:
        dict: Status of the upload and processing
    """
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are accepted"
            )
        
        # Save the file
        file_path = Path(RESUMES_DIR) / file.filename
        
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the file
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
            
        # Get OpenAI API key from environment
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key not configured"
            )
            
        # Create manager and add resume to database
        manager = VectorDBManager.load_existing(openai_api_key)
        success = manager.add_single_resume(file.filename)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to process resume"
            )
            
        return {
            "message": "Resume uploaded and processed successfully",
            "filename": file.filename
        }
        
    except Exception as e:
        # Clean up file if it was saved
        if 'file_path' in locals():
            try:
                os.remove(file_path)
            except:
                pass
                
        raise HTTPException(
            status_code=500,
            detail=f"Error processing resume: {str(e)}"
        )

@router.post("/upload/stream")
async def upload_and_stream_resume(
    file: UploadFile = File(...),
    searcher: VectorDBSearcher = Depends(get_searcher)
):
    """Upload a resume and stream the processing status.
    
    Args:
        file: The uploaded PDF file
        searcher: VectorDBSearcher instance (injected via dependency)
        
    Returns:
        StreamingResponse: A stream of status updates
    """
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are accepted"
            )
        
        # Save the file
        file_path = Path(RESUMES_DIR) / file.filename
        
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the file
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        async def process_resume():
            try:
                # Stream the processing status
                for status in run_resume_wizard(file.filename, stream=True):
                    yield f"data: {json.dumps({'status': status})}\n\n"
                    
                # After processing, add to vector database
                openai_api_key = os.getenv("OPENAI_API_KEY")
                if not openai_api_key:
                    yield f"data: {json.dumps({'error': 'OpenAI API key not configured'})}\n\n"
                    return
                    
                manager = VectorDBManager.load_existing(openai_api_key)
                success = manager.add_single_resume(file.filename)
                
                if success:
                    yield f"data: {json.dumps({'status': '✅ Resume added to database successfully!'})}\n\n"
                else:
                    yield f"data: {json.dumps({'error': 'Failed to add resume to database'})}\n\n"
                    
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                
                # Clean up file if there was an error
                try:
                    os.remove(file_path)
                except:
                    pass

        return StreamingResponse(
            process_resume(),
            media_type="text/event-stream"
        )
        
    except Exception as e:
        # Clean up file if it was saved
        if 'file_path' in locals():
            try:
                os.remove(file_path)
            except:
                pass
                
        raise HTTPException(
            status_code=500,
            detail=f"Error processing resume: {str(e)}"
        )
