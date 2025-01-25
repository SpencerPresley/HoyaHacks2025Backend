"""Dependencies for FastAPI routes."""
from resume_wizard.vectordb.searcher import VectorDBSearcher

# Global searcher instance
_searcher: VectorDBSearcher | None = None

def set_searcher(searcher: VectorDBSearcher):
    """Set the global searcher instance."""
    global _searcher
    _searcher = searcher

async def get_searcher() -> VectorDBSearcher:
    """Dependency to get VectorDBSearcher instance."""
    if _searcher is None:
        raise RuntimeError("Searcher not initialized")
    return _searcher 