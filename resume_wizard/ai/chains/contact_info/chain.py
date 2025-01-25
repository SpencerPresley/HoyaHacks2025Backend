"""Chain for extracting contact information from resumes."""
from __future__ import annotations

from typing import Any, TYPE_CHECKING

from langchain_anthropic.chat_models import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnablePassthrough

from .tools import create_contact_info_tools
from resume_wizard.ai_helpers.concrete_tools.res_parser import _ResumeParsingTools


CONTACT_INFO_PROMPT = """You are an expert at extracting contact information from resumes.
Your task is to find and extract:
1. Full name
2. Email address
3. Phone number
4. LinkedIn profile URL (if present)
5. GitHub profile URL (if present)

Guidelines:
- Extract information exactly as it appears in the resume
- Do not make assumptions or guess missing information
- If a piece of information is not found, do not include it
- For phone numbers, maintain the exact format found in the resume
- For URLs, include the complete URL as found in the resume

Process:
1. First analyze the text to find all relevant information
2. Use set_contact_info to save name, email, and phone
3. After set_contact_info succeeds, use set_social_links to save LinkedIn and GitHub URLs
4. After all tools complete, give a final summary of what was found and saved

Important: After each tool call completes successfully, continue with the next step. Do not stop until you've completed all steps."""

def create_contact_info_chain(
    api_key: str,
    parser_tools: _ResumeParsingTools,
) -> RunnablePassthrough:
    """Create a chain for extracting contact information from resumes."""
    # Create the tools
    tools = create_contact_info_tools(parser_tools)
    
    # Initialize Claude without tools
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        anthropic_api_key=api_key,
        max_tokens=4096,
    )
    
    # Bind tools to the LLM
    llm_with_tools = llm.bind_tools(tools)
    
    # Add system message
    llm_with_tools = llm_with_tools.with_config({
        "system_message": SystemMessage(content=CONTACT_INFO_PROMPT)
    })
    
    return llm_with_tools

def extract_contact_info(
    chain: RunnablePassthrough,
    resume_text: str
) -> str:
    """Extract contact information from a resume text."""
    messages = [
        {"role": "user", "content": f"Please extract contact information from this resume:\n\n{resume_text}"}
    ]
    
    while True:
        # Get next response
        response = chain.invoke(messages)
        
        print(f"\nRESPONSE:")
        print(f"Content: {response.content}")
        print(f"Metadata: {response.response_metadata}")
        
        # Add assistant's response to messages
        messages.append({"role": "assistant", "content": response.content})
        
        # If no more tool calls, we're done
        if response.response_metadata.get('stop_reason') != "tool_use":
            break
            
        # Get the tool use block
        tool_use = next(block for block in response.content if block.get('type') == "tool_use")
        
        print(f"\nTOOL USE:")
        print(f"Tool: {tool_use}")
        
        # Add tool result to messages
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use['id'],
                    "content": "Tool executed successfully"
                }
            ]
        })
    
    # Get the final text, handling both string and block content
    if isinstance(response.content, str):
        return response.content
    else:
        return next(
            (block['text'] for block in response.content if block.get('type') == 'text'),
            None
        )