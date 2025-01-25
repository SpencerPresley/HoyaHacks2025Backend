from __future__ import annotations

import os
from typing import TYPE_CHECKING
from dotenv import load_dotenv
from langchain_anthropic.chat_models import ChatAnthropic
from resume_wizard.ai.chains.contact_info.chain import extract_contact_info
from resume_wizard.pdf_parsers import parse_single_pdf
from resume_wizard.ai import create_contact_info_chain
from resume_wizard.ai.tools import _ResumeParsingTools, _ResumeParserHelper

if TYPE_CHECKING:
    from langchain.docstore.document import Document

document: Document = parse_single_pdf("spencer-presley-resume.pdf")[0]

load_dotenv()

# Create the helper and tools
helper = _ResumeParserHelper()
tools = _ResumeParsingTools(parser_helper=helper)

chain = create_contact_info_chain(
    os.getenv("ANTHROPIC_API_KEY"),
    tools
)

conversation = extract_contact_info(chain, document.page_content)
print("\nFull Conversation:\n")
print(conversation)