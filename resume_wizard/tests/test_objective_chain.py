from __future__ import annotations

import os
import json
from typing import TYPE_CHECKING
from dotenv import load_dotenv
from langchain_anthropic.chat_models import ChatAnthropic
from resume_wizard.ai.chains.objective.chain import extract_objective
from resume_wizard.pdf_parsers import parse_single_pdf
from resume_wizard.ai import create_objective_chain
from resume_wizard.ai.tools import _ResumeParsingTools, _ResumeParserHelper

if TYPE_CHECKING:
    from langchain.docstore.document import Document

document: Document = parse_single_pdf("spencer-presley-resume.pdf")[0]

load_dotenv()

# Create the helper and tools
helper = _ResumeParserHelper()
tools = _ResumeParsingTools(parser_helper=helper)

chain = create_objective_chain(
    os.getenv("ANTHROPIC_API_KEY"),
    tools
)

conversation = extract_objective(chain, document.page_content, tools)
print("\nFull Conversation:\n")
print(conversation)

# Build and print the final resume schema
print("\nFinal Resume Schema:\n")
resume = tools.build_resume()
print(json.dumps(resume.model_dump(), indent=2)) 