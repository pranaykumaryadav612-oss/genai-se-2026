#!/usr/bin/env python3
"""
Jira AI Engine - Auto Push to GitHub
=====================================
This script takes a Jira ticket as input and automatically creates a PR on GitHub.

Usage:
    python create_pr.py
    # Then enter your Jira ticket text

    # Or pass ticket text as argument:
    python create_pr.py "Your Jira ticket text here"
"""

import sys
from jira_ai_engine.main import run_pipeline, print_section

def get_ticket_from_user():
    """Get Jira ticket text from user input."""
    print("=" * 60)
    print("  JIRA AI ENGINE - Auto Push to GitHub")
    print("=" * 60)
    print()
    print("Enter your Jira ticket/question below:")
    print("(Press Enter on an empty line to submit)")
    print("-" * 50)
    
    lines = []
    while True:
        try:
            line = input()
            if line.strip() == "":
                break
            lines.append(line)
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\n\nCancelled.")
            return None
    
    return "\n".join(lines).strip()


def main():
    """Main entry point for auto PR creation."""
    
    # Get ticket text
    if len(sys.argv) > 1:
        ticket_text = " ".join(sys.argv[1:])
    else:
        ticket_text = get_ticket_from_user()
    
    if not ticket_text:
        print("No ticket text provided. Exiting.")
        sys.exit(1)
    
    # Get optional project context
    print("-" * 50)
    try:
        context_input = input("Project context (optional, press Enter to skip): ").strip()
    except (EOFError, KeyboardInterrupt):
        context_input = ""
    
    # Confirm PR creation
    print()
    print("=" * 60)
    print("⚠️  This will create a PR on GitHub!")
    print("=" * 60)
    try:
        confirm = input("Continue? (y/n): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        confirm = "n"
    
    if confirm != 'y':
        print("Cancelled.")
        sys.exit(0)
    
    # Run pipeline with dry_run=False to create actual PR
    print()
    print_section("STARTING AUTO-PUSH", "Jira Ticket → GitHub PR")
    
    results = run_pipeline(
        ticket_text=ticket_text,
        project_context=context_input,
        dry_run=False  # IMPORTANT: This will create a real PR!
    )
    
    # Final summary
    print()
    print("=" * 60)
    if results.get("success"):
        pr_info = results.get("stages", {}).get("pr", {})
        if pr_info.get("success"):
            print("✅ SUCCESS! PR Created on GitHub")
            print(f"   URL: {pr_info.get('pr_url', 'N/A')}")
            print(f"   PR #: {pr_info.get('pr_number', 'N/A')}")
            print(f"   Branch: {pr_info.get('branch', 'N/A')}")
            sys.exit(0)
        else:
            print("❌ Pipeline completed but PR creation failed")
            print(f"   Error: {pr_info.get('error', 'Unknown')}")
            sys.exit(1)
    else:
        print("❌ Pipeline failed!")
        print(f"   Error: {results.get('error', 'Unknown')}")
        sys.exit(1)


if __name__ == "__main__":
    main()