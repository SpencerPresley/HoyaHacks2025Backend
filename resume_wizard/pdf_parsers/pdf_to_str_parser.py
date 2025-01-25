from __future__ import annotations

from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader

from typing import List, TYPE_CHECKING

from resume_wizard.globals import get_absolute_path_to_resume

if TYPE_CHECKING:
    from langchain.docstore.document import Document

def parse_single_pdf(file_name: str) -> List[Document]:
    """Parse a single PDF and return a list of documents.

    Args:
        pdf_path (Path): The path to the PDF file to parse.

    Returns:
        List[Document]: A list of documents.
    """
    loader = PyMuPDFLoader(get_absolute_path_to_resume(file_name))
    docs: List[Document] = loader.load()
    return docs

def parse_multiple_pdfs(file_names: List[str]) -> List[List[Document]]:
    """Parse multiple PDFs and return a list of lists of documents.

    Args:
        file_names (List[str]): A list of file names to parse.

    Returns:
        List[List[Document]]: A list of lists of documents.
    
    Notes: 
    
    - The reason the return type is a list of lists of documents is that PyMuPDFLoader may return multiple documents for a single file.
    - The list of lists is returned so that the caller can easily access the documents for each file.
    - Each index in the list of lists corresponds to a file and all the documents created for that file are stored in the list at that index.
    """
    docs_list: List[List[Document]] = []
    for file_name in file_names:
        docs_list.append(parse_single_pdf(file_name))
    return docs_list
