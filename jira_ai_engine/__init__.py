# Jira AI Engine Package
"""
Jira AI Engine - Transform Jira tickets into code and pull requests.

Core Philosophy:
- "Jira → Code → PR"
- "Reduce manual engineering work"
- "From requirement to implementation"

Modules:
- parser: Unstructured → structured data, extract intent from text
- decision: Ticket classification, file selection, smallest change analysis
- generator: Scaffold-based code generation with templates
- github_pr: Automated PR creation with meaningful descriptions
"""

__version__ = "1.0.0"
__author__ = "Jira AI Engine Team"

from .parser import parse_ticket, validate_parsed_data, enhance_with_context
from .decision import decide_action, get_decision_summary
from .generator import generate_code, generate_multiple_files, generate_tests
from .github_pr import create_pr, validate_github_connection, get_repo_info
from .main import run_pipeline, interactive_mode, cli_mode

__all__ = [
    # Parser
    "parse_ticket",
    "validate_parsed_data",
    "enhance_with_context",
    # Decision
    "decide_action",
    "get_decision_summary",
    # Generator
    "generate_code",
    "generate_multiple_files",
    "generate_tests",
    # GitHub PR
    "create_pr",
    "validate_github_connection",
    "get_repo_info",
    # Main
    "run_pipeline",
    "interactive_mode",
    "cli_mode",
]