"""Chain for extracting career objective from resumes."""
from __future__ import annotations

from typing import Any, TYPE_CHECKING

from langchain_anthropic.chat_models import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnablePassthrough

from .tools import create_objective_tools
from resume_wizard.ai_helpers.concrete_tools.res_parser import _ResumeParsingTools


OBJECTIVE_PROMPT = """You are an expert at extracting career objectives and professional summaries from resumes.

Your task is to find and extract the career objective or professional summary section from the resume.

Guidelines:
- Look for sections titled "Objective", "Summary", "Professional Summary", etc.
- Extract the complete text of the objective/summary
- Maintain the original wording and formatting
- If multiple sections exist, combine them appropriately
- If no clear objective/summary exists, do not make one up

Process:
1. First analyze the text to find any objective or summary sections
2. Use set_objective to save the extracted text
3. After saving, provide a final summary of what was found

Important: After the tool call completes successfully, provide a final summary of what was extracted and saved."""


def create_objective_chain(
    api_key: str,
    parser_tools: _ResumeParsingTools,
) -> RunnablePassthrough:
    """Create a chain for extracting career objective from resumes."""
    # Create the tools
    tools = create_objective_tools(parser_tools)
    
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
        "system_message": SystemMessage(content=OBJECTIVE_PROMPT)
    })
    
    return llm_with_tools


def extract_objective(
    chain: RunnablePassthrough,
    resume_text: str,
    parser_tools: _ResumeParsingTools
) -> str:
    """Extract career objective from resume text."""
    print("\n=== Starting Objective Extraction ===")
    
    messages = [
        {"role": "user", "content": f"Please extract the career objective or professional summary from this resume:\n\n{resume_text}"}
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
            
        # Get the tool use block
        tool_use = next(block for block in response.content if block.get('type') == "tool_use")
        
        print("\n=== Executing Tool ===")
        print(f"Tool Name: {tool_use['name']}")
        print(f"Tool Input: {tool_use['input']}")
        
        # Actually execute the tool
        tool_name = tool_use['name']
        tool_args = tool_use['input']
        
        if tool_name == 'set_objective':
            print("Calling set_objective...")
            result = parser_tools.set_objective(**tool_args)
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