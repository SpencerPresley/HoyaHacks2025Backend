"""Chain for extracting all skills from resumes."""
from __future__ import annotations

from typing import Any, TYPE_CHECKING

from langchain_anthropic.chat_models import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnablePassthrough

from .tools import create_skills_tools
from resume_wizard.ai_helpers.concrete_tools.res_parser import _ResumeParsingTools


SKILLS_PROMPT = """You are an expert at identifying and categorizing technical and professional skills from resumes.

Your task is to find and extract all skills mentioned throughout the resume, categorizing them appropriately.

Categories to identify:
1. Programming Languages (Python, Java, etc.)
2. Frameworks (React, Django, etc.)
3. Development Tools (Git, Docker, etc.)
4. Databases (PostgreSQL, MongoDB, etc.)
5. Libraries (NumPy, Pandas, etc.)
6. Cloud Platforms (AWS, Azure, etc.)
7. Methodologies (Agile, Scrum, etc.)
8. Soft Skills (Leadership, Communication, etc.)
9. Other Technical Skills (that don't fit above categories)

Guidelines:
- Look for skills in all sections (skills, projects, experience, etc.)
- Categorize each skill appropriately using the specific tool for that category
- Extract skills exactly as they appear in the resume
- If a skill appears multiple times, only include it once
- Do not make assumptions or add skills not explicitly mentioned
- Distinguish between similar items (e.g., Python is a language, Django is a framework)

Process:
1. First analyze the entire text to identify all skills
2. Use the appropriate tool for each category:
   - add_programming_languages for languages
   - add_technical_skills with "frameworks" for frameworks
   - add_technical_skills with "dev_tools" for development tools
   - add_technical_skills with "databases" for databases
   - add_technical_skills with "libraries" for libraries
   - add_technical_skills with "cloud_platforms" for cloud platforms
   - add_technical_skills with "methodologies" for methodologies
   - add_soft_skills for soft skills
   - add_technical_skills with "other" for other technical skills
3. After saving all categories, provide a final summary of what was found

Important: After all tool calls complete successfully, provide a final summary of what skills were found and saved in each category."""


def create_skills_chain(
    api_key: str,
    parser_tools: _ResumeParsingTools,
) -> RunnablePassthrough:
    """Create a chain for extracting all skills from resumes."""
    # Create the tools
    tools = create_skills_tools(parser_tools)
    
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
        "system_message": SystemMessage(content=SKILLS_PROMPT)
    })
    
    return llm_with_tools


def extract_skills(
    chain: RunnablePassthrough,
    resume_text: str,
    parser_tools: _ResumeParsingTools
) -> str:
    """Extract all skills from resume text."""
    print("\n=== Starting Skills Extraction ===")
    
    messages = [
        {"role": "user", "content": f"Please extract and categorize all skills mentioned in this resume:\n\n{resume_text}"}
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
        
        if tool_name == 'add_programming_languages':
            print("Calling add_programming_languages...")
            result = parser_tools.add_programming_languages(**tool_args)
        elif tool_name == 'add_technical_skills':
            print("Calling add_technical_skills...")
            result = parser_tools.add_technical_skills(**tool_args)
        elif tool_name == 'add_soft_skills':
            print("Calling add_soft_skills...")
            result = parser_tools.add_soft_skills(**tool_args)
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