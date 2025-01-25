"""Chain for extracting project information from resumes."""
from __future__ import annotations

from typing import Any, TYPE_CHECKING
import json

from langchain_anthropic.chat_models import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnablePassthrough

from .tools import create_project_tools
from resume_wizard.ai_helpers.concrete_tools.res_parser import _ResumeParsingTools

PROJECTS_PROMPT = """You are an expert at analyzing resumes and extracting project information. Your task is to extract details about all projects mentioned in the resume.

For each project you find, you should:

1. First extract and add the core details using add_project:
   - Project name/title
   - Description and impact
   - Project URL/repository link (if available)
   - Timeframe/duration
   - Individual's role/contribution
   - Team size (if mentioned)
   - Project status (completed, ongoing, etc.)

2. Then add additional details using add_project_details:
   - Technologies used (programming languages, frameworks, tools)
   - Keywords describing features and outcomes

Guidelines:
- Look for projects in all sections (not just a projects section)
- Include both personal and academic projects
- Extract information exactly as it appears in the resume
- For each project:
  1. First use add_project for core details
  2. Then use add_project_details for technologies and keywords
- Pay attention to:
  - Project scope and impact
  - Technical implementation details
  - Role and responsibilities
  - Measurable outcomes
- Don't make assumptions about information not explicitly stated

Process:
1. First analyze the text to identify all projects
2. For each project found:
   a. Extract and save core details using add_project
   b. Extract and save additional details using add_project_details
3. After saving all entries, provide a final summary

Important: After all tool calls complete successfully, provide a final summary of what projects were found and saved."""

def create_projects_chain(
    api_key: str,
    parser_tools: _ResumeParsingTools,
) -> RunnablePassthrough:
    """Create a chain for extracting project information from resumes."""
    # Create the tools
    tools = create_project_tools(parser_tools)
    
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
        "system_message": SystemMessage(content=PROJECTS_PROMPT)
    })
    
    return llm_with_tools

def extract_projects(
    chain: RunnablePassthrough,
    resume_text: str,
    parser_tools: _ResumeParsingTools
) -> str:
    """Extract project information from resume text."""
    print("\n=== Starting Projects Extraction ===")
    
    messages = [
        HumanMessage(content=f"Please extract all project information from this resume:\n\n{resume_text}")
    ]
    
    print("\n=== Initial Message History ===")
    for msg in messages:
        print(f"{msg.__class__.__name__}: {msg.content[:100]}...")
    
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
        messages.append(AIMessage(content=response.content))
        
        print("\n=== Current Message History ===")
        for msg in messages:
            print(f"{msg.__class__.__name__}: {str(msg.content)[:100]}...")
        
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
            if tool_name == "add_project":
                result = parser_tools.add_project(**tool_args)
            elif tool_name == "add_project_details":
                result = parser_tools.add_project_details(**tool_args)
            else:
                result = f"Unknown tool: {tool_name}"
                
            print(f"Tool Result: {result}")
            
            # Add tool result to messages
            messages.append(HumanMessage(content=[{
                "type": "tool_result",
                "tool_use_id": tool_use['id'],
                "content": result
            }]))
            
            print("\n=== Added Tool Result ===")
            print(f"Tool Result Message: {messages[-1]}")
    
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