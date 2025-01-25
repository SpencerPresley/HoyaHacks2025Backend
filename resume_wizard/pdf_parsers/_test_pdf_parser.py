from __future__ import annotations

import os
import json
from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from langchain.docstore.document import Document

THIS_DIR = Path(__file__).parent
PARENT_DIR = THIS_DIR.parent
RESUMES_DIR = PARENT_DIR / "resumes"

def get_pdf_paths():
    return RESUMES_DIR.glob("*.pdf")

def load_pdfs():
    loaded_docs = []
    pdf_paths = get_pdf_paths()
    for pdf_path in pdf_paths:
        loader = PyMuPDFLoader(pdf_path)
        docs: List[Document] = loader.load()
        page_content: bool = True
        for doc in docs:
            if doc.page_content is None or doc.page_content == "":
                page_content = False
                break
        if page_content:
            loaded_docs.append(docs)
    return loaded_docs

if __name__ == "__main__":
    docs_list: list[Document] = load_pdfs()
    print(f"Loaded {len(docs_list)} documents")
    for i, docs in enumerate(docs_list):
        print(f"Document {i+1}:\n")
        for doc in docs:
            print(f"Page Contents:\n\n{doc.page_content}\n\n")
            print(f"Metadata:\n\n{json.dumps(doc.metadata, indent=4)}\n\n")
            print("\n\n")
            input()