"""
Parser Module - Input Understanding
"Unstructured → structured data"
"Extract intent from text"
"Acceptance criteria parsing"
"What does the user actually want?"
"""

import os
import json
import re
from typing import Dict, List, Any, Optional
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")

client = Groq(api_key=GROQ_API_KEY)


def extract_keywords(text: str) -> Dict[str, Any]:
    """Extract key information from ticket text using pattern matching."""
    keywords = {
        "has_acceptance_criteria": bool(re.search(r'acceptance\s+criteria|given\s+when|test\s+case', text, re.IGNORECASE)),
        "has_technical_details": bool(re.search(r'api|endpoint|database|query|function|class|method|component', text, re.IGNORECASE)),
        "has_user_story": bool(re.search(r'as\s+a\s+.+\s+i\s+want|user\s+story', text, re.IGNORECASE)),
        "has_error_details": bool(re.search(r'error|exception|bug|fail|crash|stack\s+trace', text, re.IGNORECASE)),
        "estimated_complexity": "low" if len(text.split()) < 100 else "medium" if len(text.split()) < 300 else "high"
    }
    return keywords


def parse_ticket(ticket_text: str) -> Dict[str, Any]:
    """
    Convert Jira ticket into structured JSON data.
    
    Extracts:
    - type: bug / feature / refactor / task
    - feature: main feature description
    - components: affected components/files
    - validations: acceptance criteria and test cases
    - intent: what the user actually wants
    - priority: inferred priority level
    """
    
    # First, extract basic keywords
    keywords = extract_keywords(ticket_text)
    
    prompt = f"""You are an expert software engineer analyzing a Jira ticket. 
Convert this unstructured ticket into structured data.

**Analysis Framework:**
1. What type of ticket is this? (bug / feature / refactor / task)
2. What does the user actually want? (extract the core intent)
3. What files/components should change?
4. What are the acceptance criteria?

**Ticket Text:**
{ticket_text}

**Output Format (strict JSON):**
{{
    "type": "bug|feature|refactor|task",
    "title": "concise title",
    "feature": "detailed feature description",
    "intent": "what the user actually wants to achieve",
    "components": ["list", "of", "affected", "components"],
    "files_to_change": ["suggested", "files", "to", "modify"],
    "acceptance_criteria": ["criterion 1", "criterion 2"],
    "validations": ["test cases or validation steps"],
    "priority": "low|medium|high|critical",
    "complexity": "low|medium|high",
    "is_smallest_change": "description of the smallest possible change",
    "technical_notes": "any technical considerations"
}}

Return ONLY valid JSON, no markdown formatting."""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a precise JSON formatter. Always return valid JSON without markdown."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        content = response.choices[0].message.content
        
        # Clean up the response (remove markdown code blocks if present)
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'\s*```', '', content)
        content = content.strip()
        
        parsed_data = json.loads(content)
        
        # Add extracted keywords
        parsed_data["extracted_keywords"] = keywords
        parsed_data["original_ticket"] = ticket_text[:500]  # Store truncated original
        
        return parsed_data
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Raw response: {content}")
        return {
            "type": "task",
            "feature": ticket_text[:200],
            "components": [],
            "validations": [],
            "intent": "Could not parse ticket automatically",
            "error": str(e),
            "raw_response": content
        }
    except Exception as e:
        print(f"Error parsing ticket: {e}")
        return {
            "type": "task",
            "feature": ticket_text[:200],
            "components": [],
            "validations": [],
            "intent": "Error during parsing",
            "error": str(e)
        }


def validate_parsed_data(parsed_data: Dict[str, Any]) -> bool:
    """Validate that parsed data has required fields."""
    required_fields = ["type", "feature", "components", "validations"]
    return all(field in parsed_data for field in required_fields)


def enhance_with_context(parsed_data: Dict[str, Any], project_context: str = "") -> Dict[str, Any]:
    """
    Enhance parsed data with additional project context.
    "From requirement to implementation"
    """
    if not project_context:
        return parsed_data
    
    prompt = f"""Given this parsed Jira ticket and project context, enhance the analysis:

**Parsed Ticket:**
{json.dumps(parsed_data, indent=2)}

**Project Context:**
{project_context}

**Questions to answer:**
1. What is the smallest possible change?
2. What reusable patterns exist in this codebase?
3. Should this be scaffold code or final code?

Return enhanced JSON with additional fields: smallest_change, reusable_patterns, code_approach"""
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a precise JSON formatter."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1500
        )
        
        content = response.choices[0].message.content
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'\s*```', '', content)
        
        enhancements = json.loads(content)
        parsed_data.update(enhancements)
        return parsed_data
        
    except Exception as e:
        print(f"Enhancement error: {e}")
        return parsed_data