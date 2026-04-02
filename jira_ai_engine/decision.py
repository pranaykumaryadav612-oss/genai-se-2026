"""
Decision Module - Decision Layer
"What type of ticket is this?"
"What files should change?"
"What is the smallest possible change?"
"""

from typing import Dict, List, Any, Tuple
import json


# Decision templates for different ticket types
DECISION_TEMPLATES = {
    "bug": {
        "action": "fix",
        "approach": "minimal_change",
        "priority_boost": 1,  # Increase priority by one level
        "requires_tests": True,
        "requires_rollback_plan": True
    },
    "feature": {
        "action": "add",
        "approach": "scaffold_first",
        "priority_boost": 0,
        "requires_tests": True,
        "requires_rollback_plan": False
    },
    "refactor": {
        "action": "refactor",
        "approach": "incremental",
        "priority_boost": -1,  # Lower priority unless critical
        "requires_tests": True,
        "requires_rollback_plan": True
    },
    "task": {
        "action": "general",
        "approach": "standard",
        "priority_boost": 0,
        "requires_tests": False,
        "requires_rollback_plan": False
    }
}

# File type heuristics
FILE_HEURISTICS = {
    "api": ["controller", "route", "endpoint", "handler", "api"],
    "database": ["model", "schema", "migration", "repository", "dao"],
    "frontend": ["component", "view", "page", "ui", "template"],
    "config": ["config", "settings", "environment", "constant"],
    "test": ["test", "spec", "fixture", "mock"],
    "utility": ["util", "helper", "service", "manager"]
}


def classify_ticket_type(parsed_data: Dict[str, Any]) -> str:
    """
    Classify ticket type based on parsed data.
    "What type of ticket is this?"
    """
    ticket_type = parsed_data.get("type", "task").lower()
    
    # Validate ticket type
    valid_types = ["bug", "feature", "refactor", "task"]
    if ticket_type not in valid_types:
        # Try to infer from content
        feature_text = parsed_data.get("feature", "").lower()
        intent_text = parsed_data.get("intent", "").lower()
        
        if any(word in feature_text + intent_text for word in ["fix", "bug", "error", "crash", "fail"]):
            ticket_type = "bug"
        elif any(word in feature_text + intent_text for word in ["new", "add", "create", "implement"]):
            ticket_type = "feature"
        elif any(word in feature_text + intent_text for word in ["refactor", "improve", "optimize", "clean"]):
            ticket_type = "refactor"
        else:
            ticket_type = "task"
    
    return ticket_type


def determine_files_to_change(parsed_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Determine which files should change based on components and feature description.
    "What files should change?"
    """
    components = parsed_data.get("components", [])
    files_suggested = parsed_data.get("files_to_change", [])
    feature_desc = parsed_data.get("feature", "").lower()
    
    file_decisions = []
    
    # Process explicitly suggested files
    for file_path in files_suggested:
        file_type = infer_file_type(file_path)
        file_decisions.append({
            "file": file_path,
            "type": file_type,
            "action": "modify",
            "confidence": "high"
        })
    
    # Infer additional files from components
    for component in components:
        component_lower = component.lower()
        for file_type, keywords in FILE_HEURISTICS.items():
            if any(keyword in component_lower for keyword in keywords):
                suggested_file = f"src/{file_type}s/{component}.py"  # Generic suggestion
                if not any(f["file"] == suggested_file for f in file_decisions):
                    file_decisions.append({
                        "file": suggested_file,
                        "type": file_type,
                        "action": "modify",
                        "confidence": "medium"
                    })
    
    return file_decisions


def infer_file_type(file_path: str) -> str:
    """Infer the type of file based on its path."""
    file_path_lower = file_path.lower()
    for file_type, keywords in FILE_HEURISTICS.items():
        if any(keyword in file_path_lower for keyword in keywords):
            return file_type
    return "unknown"


def calculate_smallest_change(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate the smallest possible change to implement the requirement.
    "What is the smallest possible change?"
    """
    ticket_type = parsed_data.get("type", "task")
    complexity = parsed_data.get("complexity", "medium")
    components = parsed_data.get("components", [])
    
    smallest_change = {
        "scope": "minimal",
        "files_affected": len(components) if components else 1,
        "lines_estimate": 10 if complexity == "low" else 50 if complexity == "medium" else 100,
        "approach": DECISION_TEMPLATES.get(ticket_type, DECISION_TEMPLATES["task"])["approach"],
        "recommendation": ""
    }
    
    # Generate recommendation
    if ticket_type == "bug":
        smallest_change["recommendation"] = "Focus on the specific bug fix with minimal code changes. Add regression test."
    elif ticket_type == "feature":
        smallest_change["recommendation"] = "Start with scaffold code. Implement core functionality first, then iterate."
    elif ticket_type == "refactor":
        smallest_change["recommendation"] = "Make incremental changes. Ensure tests pass after each step."
    else:
        smallest_change["recommendation"] = "Implement the minimum viable solution that meets acceptance criteria."
    
    return smallest_change


def decide_action(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main decision function that orchestrates all decision-making.
    Returns a comprehensive decision object.
    """
    # Classify ticket type
    ticket_type = classify_ticket_type(parsed_data)
    
    # Get template for this ticket type
    template = DECISION_TEMPLATES.get(ticket_type, DECISION_TEMPLATES["task"])
    
    # Determine files to change
    file_decisions = determine_files_to_change(parsed_data)
    
    # Calculate smallest change
    smallest_change = calculate_smallest_change(parsed_data)
    
    # Adjust priority based on ticket type
    original_priority = parsed_data.get("priority", "medium")
    priority_levels = {"low": 0, "medium": 1, "high": 2, "critical": 3}
    adjusted_priority_level = priority_levels.get(original_priority, 1) + template["priority_boost"]
    adjusted_priority_level = max(0, min(3, adjusted_priority_level))
    adjusted_priority = list(priority_levels.keys())[adjusted_priority_level]
    
    # Build comprehensive decision
    decision = {
        "ticket_type": ticket_type,
        "action": template["action"],
        "approach": template["approach"],
        "priority": {
            "original": original_priority,
            "adjusted": adjusted_priority,
            "reason": f"Adjusted due to {ticket_type} classification"
        },
        "files_to_change": file_decisions,
        "smallest_change": smallest_change,
        "requires_tests": template["requires_tests"],
        "requires_rollback_plan": template["requires_rollback_plan"],
        "code_generation_strategy": determine_generation_strategy(parsed_data, template)
    }
    
    return decision


def determine_generation_strategy(parsed_data: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, Any]:
    """
    Determine the code generation strategy.
    "Scaffold, not full solution"
    "Starter code vs final code"
    "Template-based generation"
    "Reusable patterns"
    """
    approach = template["approach"]
    
    strategies = {
        "minimal_change": {
            "code_style": "focused",
            "completeness": "complete",
            "includes_comments": True,
            "includes_tests": True,
            "description": "Generate complete, focused fix with tests"
        },
        "scaffold_first": {
            "code_style": "template",
            "completeness": "partial",
            "includes_comments": True,
            "includes_tests": False,
            "description": "Generate scaffold/template code for iteration"
        },
        "incremental": {
            "code_style": "conservative",
            "completeness": "complete",
            "includes_comments": True,
            "includes_tests": True,
            "description": "Generate safe, incremental changes"
        },
        "standard": {
            "code_style": "standard",
            "completeness": "complete",
            "includes_comments": False,
            "includes_tests": False,
            "description": "Generate standard implementation"
        }
    }
    
    return strategies.get(approach, strategies["standard"])


def get_decision_summary(decision: Dict[str, Any]) -> str:
    """Generate a human-readable summary of the decision."""
    summary = f"""
=== DECISION SUMMARY ===
Ticket Type: {decision['ticket_type']}
Action: {decision['action']}
Approach: {decision['approach']}
Priority: {decision['priority']['original']} → {decision['priority']['adjusted']}

Files to Change ({len(decision['files_to_change'])}):
"""
    
    for file_dec in decision['files_to_change']:
        summary += f"  - {file_dec['file']} ({file_dec['type']}, confidence: {file_dec['confidence']})\n"
    
    summary += f"""
Smallest Change:
  Scope: {decision['smallest_change']['scope']}
  Approach: {decision['smallest_change']['approach']}
  Recommendation: {decision['smallest_change']['recommendation']}

Code Generation Strategy:
  {decision['code_generation_strategy']['description']}
  Includes Tests: {decision['requires_tests']}
  Includes Comments: {decision['code_generation_strategy']['includes_comments']}

Requires Rollback Plan: {decision['requires_rollback_plan']}
=== END SUMMARY ===
"""
    
    return summary