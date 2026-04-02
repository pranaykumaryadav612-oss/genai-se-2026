"""
Generator Module - Code Generation
"Scaffold, not full solution"
"Starter code vs final code"
"Template-based generation"
"Reusable patterns"
"""

import os
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")

client = Groq(api_key=GROQ_API_KEY)


# Code generation templates for different scenarios
CODE_TEMPLATES = {
    "bug_fix": """
# Bug Fix Template
# Issue: {issue_description}
# Root Cause: {root_cause}
# Fix: {fix_description}

{existing_code}

# Fixed code:
{fixed_code}

# Test case to prevent regression:
{test_code}
""",
    
    "feature_scaffold": """
# Feature Scaffold: {feature_name}
# Description: {description}
# This is a STARTER TEMPLATE - implement the TODO sections

class {class_name}:
    \"\"\"
    {docstring}
    \"\"\"
    
    def __init__(self):
        # TODO: Initialize component
        pass
    
    def main_method(self, input_data):
        \"\"\"
        Main method for {feature_name}
        
        Args:
            input_data: Input data to process
            
        Returns:
            Processed output
        \"\"\"
        # TODO: Implement core logic
        raise NotImplementedError("Implement this method")
    
    def helper_method(self, param):
        \"\"\"
        Helper method for {feature_name}
        \"\"\"
        # TODO: Add helper functionality
        pass


# Usage example:
# instance = {class_name}()
# result = instance.main_method(sample_data)
""",
    
    "refactor_template": """
# Refactoring: {description}
# Before: {before_description}
# After: {after_description}
# This is a safe, incremental change

{refactored_code}

# Verification steps:
# 1. Run existing tests
# 2. Check for behavior changes
# 3. Validate performance
""",

    "api_endpoint": """
# API Endpoint: {endpoint_name}
# Method: {http_method}
# Path: {path}
# Description: {description}

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class {request_model} (BaseModel):
    # TODO: Define request body fields
    pass

class {response_model} (BaseModel):
    # TODO: Define response fields
    pass

@router.{http_method_lower}("{path}", response_model={response_model})
async def {function_name}(request: {request_model}):
    \"\"\"
    {description}
    \"\"\"
    try:
        # TODO: Implement endpoint logic
        result = None
        return {response_model}(data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
""",

    "database_model": """
# Database Model: {model_name}
# Table: {table_name}
# Description: {description}

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class {class_name}(Base):
    \"\"\"
    {description}
    \"\"\"
    __tablename__ = "{table_name}"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # TODO: Add model-specific fields
    # field_name = Column(String, nullable=True)
    
    def to_dict(self):
        \"\"\"Convert model to dictionary\"\"\"
        return {{
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            # TODO: Add other fields
        }}
"""
}


def select_template(decision: Dict[str, Any], parsed_data: Dict[str, Any]) -> str:
    """Select the appropriate code template based on decision and parsed data."""
    ticket_type = decision.get("ticket_type", "task")
    action = decision.get("action", "general")
    files_to_change = decision.get("files_to_change", [])
    
    # Check for specific file types
    has_api = any(f.get("type") == "api" for f in files_to_change)
    has_database = any(f.get("type") == "database" for f in files_to_change)
    
    if ticket_type == "bug" and action == "fix":
        return "bug_fix"
    elif ticket_type == "feature":
        if has_api:
            return "api_endpoint"
        elif has_database:
            return "database_model"
        else:
            return "feature_scaffold"
    elif ticket_type == "refactor":
        return "refactor_template"
    else:
        return "feature_scaffold"


def generate_code(
    parsed_data: Dict[str, Any], 
    decision: Dict[str, Any], 
    project_context: str = ""
) -> Dict[str, Any]:
    """
    Generate code based on parsed ticket and decision.
    Returns structured output with filename and code content.
    """
    ticket_type = decision.get("ticket_type", "task")
    action = decision.get("action", "general")
    strategy = decision.get("code_generation_strategy", {})
    
    # Select template
    template_name = select_template(decision, parsed_data)
    template = CODE_TEMPLATES.get(template_name, CODE_TEMPLATES["feature_scaffold"])
    
    # Build prompt for AI code generation
    prompt = build_generation_prompt(parsed_data, decision, template, project_context)
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system", 
                    "content": """You are an expert software engineer. Generate clean, 
                    maintainable code following best practices. 
                    Focus on the smallest possible change.
                    Return code in the format:
                    filename: path/to/file.ext
                    code:
                    <actual code here>
                    """
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=3000
        )
        
        content = response.choices[0].message.content
        
        # Parse the response
        filename, code = parse_generated_code(content)
        
        return {
            "filename": filename,
            "code": code,
            "raw_response": content,
            "template_used": template_name,
            "strategy": strategy
        }
        
    except Exception as e:
        print(f"Code generation error: {e}")
        return {
            "filename": "error.py",
            "code": f"# Error during code generation: {str(e)}",
            "raw_response": str(e),
            "template_used": template_name,
            "strategy": strategy
        }


def build_generation_prompt(
    parsed_data: Dict[str, Any], 
    decision: Dict[str, Any], 
    template: str,
    project_context: str = ""
) -> str:
    """Build a comprehensive prompt for code generation."""
    
    ticket_type = decision.get("ticket_type", "task")
    action = decision.get("action", "general")
    strategy = decision.get("code_generation_strategy", {})
    files_to_change = decision.get("files_to_change", [])
    
    feature_desc = parsed_data.get("feature", "")
    intent = parsed_data.get("intent", "")
    acceptance_criteria = parsed_data.get("acceptance_criteria", [])
    components = parsed_data.get("components", [])
    
    # Build the prompt
    prompt = f"""You are implementing a code change based on a Jira ticket.

**Ticket Analysis:**
- Type: {ticket_type}
- Action: {action}
- Feature: {feature_desc}
- User Intent: {intent}
- Components: {', '.join(components) if components else 'Not specified'}

**Decision Context:**
- Files to change: {[f['file'] for f in files_to_change]}
- Approach: {decision.get('approach', 'standard')}
- Smallest change: {decision.get('smallest_change', {}).get('recommendation', '')}

**Acceptance Criteria:**
{chr(10).join(f"- {criterion}" for criterion in acceptance_criteria[:5]) if acceptance_criteria else "- None specified"}

**Code Generation Strategy:**
- Style: {strategy.get('code_style', 'standard')}
- Completeness: {strategy.get('completeness', 'complete')}
- Include comments: {strategy.get('includes_comments', False)}
- Include tests: {strategy.get('includes_tests', False)}
- Description: {strategy.get('description', '')}

**Template to use:**
{template}

**Project Context:**
{project_context if project_context else "No additional context provided"}

**Instructions:**
1. Generate code that implements the SMALLEST possible change
2. Follow the template structure but adapt to the specific requirements
3. If generating a feature, create SCAFFOLD code (starter template)
4. If fixing a bug, create a COMPLETE fix with regression test
5. If refactoring, make INCREMENTAL, safe changes
6. Return the output in this exact format:
   filename: path/to/file.py
   code:
   <your code here>

Focus on quality over quantity. Better to have a small, working piece than a large, broken one."""

    return prompt


def parse_generated_code(response: str) -> Tuple[str, str]:
    """Parse the generated code response to extract filename and code."""
    
    # Try to find filename and code sections
    filename_match = re.search(r'filename:\s*(.+)', response, re.IGNORECASE)
    code_match = re.search(r'code:\s*(.+)', response, re.IGNORECASE | re.DOTALL)
    
    if filename_match and code_match:
        filename = filename_match.group(1).strip()
        code = code_match.group(1).strip()
        return filename, code
    
    # Fallback: try to extract from markdown code blocks
    markdown_match = re.search(r'```(\w+)\s*\n(.*?)```', response, re.DOTALL)
    if markdown_match:
        language = markdown_match.group(1)
        code = markdown_match.group(2).strip()
        
        # Try to infer filename from language
        ext_map = {
            'python': 'py', 'js': 'js', 'javascript': 'js', 'ts': 'ts', 
            'typescript': 'ts', 'java': 'java', 'go': 'go', 'rust': 'rs',
            'sql': 'sql', 'html': 'html', 'css': 'css'
        }
        ext = ext_map.get(language.lower(), 'txt')
        filename = f"generated_file.{ext}"
        
        return filename, code
    
    # Last resort: return entire response as code
    return "generated_file.txt", response


def generate_tests(parsed_data: Dict[str, Any], generated_code: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Generate test code for the generated implementation."""
    
    if not generated_code.get("code"):
        return None
    
    prompt = f"""Generate unit tests for this code:

**Original Ticket:**
{parsed_data.get('feature', '')}

**Acceptance Criteria:**
{chr(10).join(f"- {c}" for c in parsed_data.get('validations', [])[:3])}

**Generated Code:**
{generated_code['code']}

**File:** {generated_code['filename']}

Generate comprehensive unit tests following these guidelines:
1. Test the happy path
2. Test edge cases mentioned in acceptance criteria
3. Include at least one negative test case
4. Use appropriate testing framework (pytest style)

Return in format:
filename: test_{generated_code['filename']}
code:
<test code here>"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a test automation expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=2000
        )
        
        content = response.choices[0].message.content
        filename, code = parse_generated_code(content)
        
        return {
            "filename": filename,
            "code": code,
            "raw_response": content
        }
        
    except Exception as e:
        print(f"Test generation error: {e}")
        return None


def generate_multiple_files(
    parsed_data: Dict[str, Any], 
    decision: Dict[str, Any],
    project_context: str = ""
) -> List[Dict[str, Any]]:
    """
    Generate multiple files if needed based on the decision.
    Returns a list of file generation results.
    """
    files_to_generate = []
    
    # Generate main code
    main_result = generate_code(parsed_data, decision, project_context)
    files_to_generate.append(main_result)
    
    # Generate tests if required
    if decision.get("requires_tests", False):
        test_result = generate_tests(parsed_data, main_result)
        if test_result:
            files_to_generate.append(test_result)
    
    return files_to_generate