"""Chain for extracting education information from resumes."""
from __future__ import annotations

from typing import Any, TYPE_CHECKING
import json

from langchain_anthropic.chat_models import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnablePassthrough

from .tools import create_education_tools
from resume_wizard.ai_helpers.concrete_tools.res_parser import _ResumeParsingTools


EDUCATION_PROMPT = """You are an expert at extracting education information from resumes.

Your task is to find and extract all education-related information throughout the resume.

Information to Extract:
1. Core Details:
   - Institution name
   - Degree/program
   - Location
   - Dates (start and end/expected)
   - GPA (if provided)

2. Additional Details:
   - Minor fields of study
   - Academic honors/distinctions
   - Relevant coursework
   - Other academic achievements/activities

Guidelines:
- Look for education information in all sections (not just education section)
- Extract details exactly as they appear in the resume
- For each institution found:
  1. First use add_education for core details
  2. Then use add_education_details for additional information
- Handle both completed and ongoing education
- Include all levels of education mentioned (university, college, certifications)
- Pay attention to formatting of dates and GPA
- Don't make assumptions about information not explicitly stated

Process:
1. First analyze the text to identify all educational institutions
2. For each institution:
   a. Extract and save core details using add_education
   b. Extract and save additional details using add_education_details
3. After saving all entries, provide a final summary

Important: After all tool calls complete successfully, provide a final summary of what education information was found and saved."""


def create_education_chain(
    api_key: str,
    parser_tools: _ResumeParsingTools,
) -> RunnablePassthrough:
    """Create a chain for extracting education information from resumes."""
    # Create the tools
    tools = create_education_tools(parser_tools)
    
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
        "system_message": SystemMessage(content=EDUCATION_PROMPT)
    })
    
    return llm_with_tools


def extract_education(
    chain: RunnablePassthrough,
    resume_text: str,
    parser_tools: _ResumeParsingTools
) -> str:
    print("\n=== Starting Education Extraction ===")
    
    messages = [
        {"role": "user", "content": f"Please extract all education information from this resume:\n\n{resume_text}"}
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
            if tool_name == "add_education":
                result = parser_tools.add_education(**tool_args)
            elif tool_name == "add_education_details":
                result = parser_tools.add_education_details(**tool_args)
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