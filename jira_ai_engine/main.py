# -*- coding: utf-8 -*-
"""
Jira AI Engine - Main Entry Point
"Jira -> Code -> PR"
"Reduce manual engineering work"
"From requirement to implementation"
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Ensure UTF-8 encoding for output
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add parent directory to path to allow running this script directly
parent_dir = Path(__file__).resolve().parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from jira_ai_engine.parser import parse_ticket, validate_parsed_data, enhance_with_context
from jira_ai_engine.decision import decide_action, get_decision_summary
from jira_ai_engine.generator import generate_multiple_files
from jira_ai_engine.github_pr import create_pr, validate_github_connection, get_repo_info


def print_section(title: str, content: str = "", separator: str = "="):
    """Print a formatted section header."""
    width = 60
    print("\n" + separator * width)
    print(f" {title}")
    print(separator * width)
    if content:
        print(content)


def print_json_pretty(data: Dict[str, Any], title: str = ""):
    """Print JSON data in a readable format."""
    if title:
        print(f"\n--- {title} ---")
    print(json.dumps(data, indent=2, default=str))


def run_pipeline(
    ticket_text: str, 
    project_context: str = "",
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Run the complete Jira → Code → PR pipeline.
    
    Args:
        ticket_text: Raw Jira ticket text
        project_context: Optional project context for better decisions
        dry_run: If True, don't actually create the PR
    
    Returns:
        Dictionary containing all pipeline results
    """
    results = {
        "ticket": ticket_text[:200],
        "stages": {},
        "success": False
    }
    
    try:
        # ==========================================
        # STAGE 1: Parse Ticket (Input Understanding)
        # ==========================================
        print_section("STAGE 1: PARSING TICKET", "Unstructured → Structured Data")
        print("Analyzing ticket content...")
        
        parsed_data = parse_ticket(ticket_text)
        results["stages"]["parsing"] = parsed_data
        
        print_json_pretty(parsed_data, "Parsed Ticket Data")
        
        # Validate parsed data
        if not validate_parsed_data(parsed_data):
            print("⚠️ Warning: Parsed data may be incomplete")
        
        # ==========================================
        # STAGE 2: Make Decisions (Decision Layer)
        # ==========================================
        print_section("STAGE 2: DECISION MAKING", "What type of ticket is this?")
        print("Analyzing and making decisions...")
        
        decision = decide_action(parsed_data)
        results["stages"]["decision"] = decision
        
        # Print human-readable summary
        decision_summary = get_decision_summary(decision)
        print(decision_summary)
        
        # ==========================================
        # STAGE 3: Generate Code (Code Generation)
        # ==========================================
        print_section("STAGE 3: CODE GENERATION", "Scaffold, not full solution")
        print("Generating code based on decisions...")
        
        generated_files = generate_multiple_files(parsed_data, decision, project_context)
        results["stages"]["generation"] = generated_files
        
        print(f"\nGenerated {len(generated_files)} file(s):")
        for i, file_info in enumerate(generated_files, 1):
            filename = file_info.get("filename", "unknown")
            code_length = len(file_info.get("code", ""))
            template = file_info.get("template_used", "unknown")
            print(f"  {i}. {filename} ({code_length} chars, template: {template})")
        
        # ==========================================
        # STAGE 4: Create PR (GitHub Integration)
        # ==========================================
        if dry_run:
            print_section("DRY RUN MODE", "Skipping PR creation")
            results["dry_run"] = True
        else:
            print_section("STAGE 4: CREATING PR", "From requirement to implementation")
            print("Validating GitHub connection...")
            
            if not validate_github_connection():
                print("❌ GitHub connection validation failed")
                results["stages"]["pr"] = {"success": False, "error": "GitHub connection failed"}
            else:
                print("GitHub connection OK")
                print("Creating PR...")
                
                pr_result = create_pr(generated_files, parsed_data, decision)
                results["stages"]["pr"] = pr_result
                
                if pr_result.get("success"):
                    print(f"\n✅ PR Created Successfully!")
                    print(f"   URL: {pr_result.get('pr_url', 'N/A')}")
                    print(f"   Number: #{pr_result.get('pr_number', 'N/A')}")
                else:
                    print(f"\n❌ PR Creation Failed: {pr_result.get('error', 'Unknown error')}")
        
        results["success"] = True
        
    except Exception as e:
        print(f"\n❌ Pipeline failed with error: {str(e)}")
        results["error"] = str(e)
        results["success"] = False
    
    # ==========================================
    # FINAL SUMMARY
    # ==========================================
    print_section("PIPELINE COMPLETE", f"Success: {results['success']}")
    
    return results


def interactive_mode():
    """Run the pipeline in interactive mode."""
    print("=" * 60)
    print("       JIRA AI ENGINE - Jira -> Code -> PR")
    print("=" * 60)
    print()
    
    print("Enter your Jira ticket text (press Enter twice to finish):")
    print("-" * 50)
    
    lines = []
    empty_line_count = 0
    
    while True:
        try:
            line = input()
            if line.strip() == "":
                empty_line_count += 1
                if empty_line_count >= 2:
                    break
            else:
                empty_line_count = 0
                lines.append(line)
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
            return None
    
    ticket_text = "\n".join(lines).strip()
    
    if not ticket_text:
        print("No ticket text provided. Exiting.")
        return None
    
    # Ask for project context
    print("-" * 50)
    try:
        context_input = input("Enter project context (optional, press Enter to skip): ").strip()
    except (EOFError, KeyboardInterrupt):
        context_input = ""
    
    # Ask for dry run
    print("-" * 50)
    try:
        dry_run_input = input("Dry run mode? (y/n, default: n): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        dry_run_input = "n"
    dry_run = dry_run_input == 'y'
    
    # Run pipeline
    print("-" * 50)
    print("Processing ticket...")
    print()
    results = run_pipeline(ticket_text, context_input, dry_run)
    
    return results


def cli_mode(ticket_text: str, context: str = "", dry_run: bool = False):
    """Run the pipeline from command line arguments."""
    return run_pipeline(ticket_text, context, dry_run)


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # CLI mode: pass ticket text as argument
        ticket_text = " ".join(sys.argv[1:])
        results = cli_mode(ticket_text)
    else:
        # Interactive mode
        results = interactive_mode()
    
    # Exit with appropriate code
    sys.exit(0 if results.get("success") else 1)


if __name__ == "__main__":
    main()