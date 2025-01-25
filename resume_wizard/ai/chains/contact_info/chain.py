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
    resume_text: str,
    parser_tools: _ResumeParsingTools
) -> str:
    """Extract contact information from a resume text."""
    print("\n=== Starting Contact Info Extraction ===")
    
    messages = [
        {"role": "user", "content": f"Please extract contact information from this resume:\n\n{resume_text}"}
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
                    print(f"Tool Use ID: {block['id']}")
        
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
            print(f"\nTool Use ID from block: {tool_use['id']}")
            
            print("\n=== Executing Tool ===")
            print(f"Tool Name: {tool_use['name']}")
            print(f"Tool Input: {tool_use['input']}")
            
            # Actually execute the tool
            tool_name = tool_use['name']
            tool_args = tool_use['input']
            
            if tool_name == 'set_contact_info':
                print("Calling set_contact_info...")
                # Ensure phone has a default value of None
                if 'phone' not in tool_args:
                    tool_args['phone'] = None
                result = parser_tools.set_contact_info(**tool_args)
            elif tool_name == 'set_social_links':
                print("Calling set_social_links...")
                result = parser_tools.set_social_links(**tool_args)
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
            print(f"Tool Use ID in result: {tool_message['content'][0]['tool_use_id']}")
    
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