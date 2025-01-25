"""Chain for extracting experience information from resumes."""
from __future__ import annotations

from typing import Any, TYPE_CHECKING
import json

from langchain_anthropic.chat_models import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnablePassthrough

from .tools import create_experience_tools
from resume_wizard.ai_helpers.concrete_tools.res_parser import _ResumeParsingTools

EXPERIENCE_PROMPT = """You are an expert at analyzing resumes and extracting professional experience information. Your task is to extract work experience details from the provided resume text.

For each work experience entry you find, you should:

1. First extract and add the core details using add_experience:
   - Position/title
   - Company name
   - Initial description of responsibilities
   - Location (if available)
   - Start and end dates
   - Whether it's a current position
   - Position type (full-time, part-time, internship, etc.)

2. Then add additional details using add_experience_details:
   - Industry sector
   - More detailed description of responsibilities
   - Quantifiable achievements and results
   - Key terms/keywords related to the role
   - Technical tools and technologies used

Extract the experience entries in chronological order (most recent first). Be thorough in capturing all relevant details, especially achievements and technologies used.

Guidelines:
- For the initial add_experience call, include a basic description of the role
- Use add_experience_details to expand on the description and add more specific details
- Extract information exactly as it appears in the resume
- Include all positions mentioned (full-time, part-time, internships)
- Pay attention to dates and position types
- Don't make assumptions about information not explicitly stated

Resume Text:
{resume_text}

Extract the experience information from this resume text. Use the provided tools to add each experience entry and its details."""

def create_experience_chain(
    api_key: str,
    parser_tools: _ResumeParsingTools,
) -> RunnablePassthrough:
    """Create a chain for extracting experience information from resumes."""
    # Create the tools
    tools = create_experience_tools(parser_tools)
    
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
        "system_message": SystemMessage(content=EXPERIENCE_PROMPT)
    })
    
    return llm_with_tools

def extract_experience(
    chain: RunnablePassthrough,
    resume_text: str,
    parser_tools: _ResumeParsingTools
) -> str:
    print("\n=== Starting Experience Extraction ===")
    
    messages = [
        {"role": "user", "content": f"Please extract all experience information from this resume:\n\n{resume_text}"}
    ]
    
    print("\n=== Initial Message History ===")
    for msg in messages:
        print(f"{msg['role'].upper()}: {msg['content'][:100]}...")
    
    while True:
        print("\n=== Getting Next Response ===")
        response = chain.invoke(messages)
        
        print("\n=== Response Details ===")
        print(f"Stop Reason: {response.response_metadata.get('stop_reason')}")
        print(f"Content Type: {type(response.content)}")
        if isinstance(response.content, list):
            for block in response.content:
                print(f"Block Type: {block.get('type')}")
                if block.get('type') == 'text':
                    print(f"Text: {block['text']}")
                elif block.get('type') == 'tool_use':
                    print(f"Tool: {block['name']}")
                    print(f"Input: {block['input']}")
        
        # Add assistant's response to messages
        messages.append({"role": "assistant", "content": response.content})
        
        print("\n=== Current Message History ===")
        for msg in messages:
            print(f"{msg['role'].upper()}: {str(msg['content'])[:100]}...")
        
        # If no more tool calls, we're done
        if response.response_metadata.get('stop_reason') != "tool_use":
            print("\n=== Conversation Complete ===")
            break
            
        # Get all tool use blocks
        tool_uses = [block for block in response.content if block.get('type') == "tool_use"]
        
        # Process each tool use
        for tool_use in tool_uses:
            print("\n=== Executing Tool ===")
            print(f"Tool Name: {tool_use['name']}")
            print(f"Tool Input: {tool_use['input']}")
            
            # Actually execute the tool
            tool_name = tool_use['name']
            tool_args = tool_use['input']
            
            print(f"\nExecuting tool: {tool_name}")
            print(f"Tool Input: {tool_args}")
            print("Calling " + tool_name + "...")
            
            # Execute the tool
            if tool_name == "add_experience":
                result = parser_tools.add_experience(**tool_args)
            elif tool_name == "add_experience_details":
                result = parser_tools.add_experience_details(**tool_args)
            else:
                result = f"Unknown tool: {tool_name}"
                
            print(f"Tool Result: {result}")
            
            # Add tool result to messages
            tool_message = {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use['id'],
                        "content": result
                    }
                ]
            }
            messages.append(tool_message)
            
            print("\n=== Added Tool Result ===")
            print(f"Tool Result Message: {tool_message}")
    
    print("\n=== Final Response ===")
    if isinstance(response.content, str):
        print(f"String Content: {response.content}")
        return response.content
    else:
        final_text = next(
            (block['text'] for block in response.content if block.get('type') == 'text'),
            None
        )
        print(f"Block Content: {final_text}")
        return final_text 