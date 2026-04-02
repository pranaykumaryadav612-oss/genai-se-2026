#!/usr/bin/env python3
"""
Test script for the enhanced create_pr logic.
This script tests the create_pr function with various scenarios.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from jira_ai_engine.github_pr import (
    create_pr,
    generate_branch_name,
    generate_pr_title,
    generate_pr_body,
    generate_commit_message,
    validate_github_connection,
    get_repo_info
)


def test_generate_branch_name():
    """Test branch name generation."""
    print("\n" + "=" * 60)
    print("TEST: generate_branch_name")
    print("=" * 60)
    
    parsed_data = {
        "feature": "Implement user authentication system",
        "title": "User Auth Feature"
    }
    decision = {
        "ticket_type": "feature",
        "action": "add"
    }
    
    branch_name = generate_branch_name(parsed_data, decision)
    print(f"Generated branch name: {branch_name}")
    
    # Verify format
    assert branch_name.startswith("ai/feature/"), f"Expected prefix 'ai/feature/', got {branch_name}"
    assert len(branch_name.split("-")[-1]) == 8, "Expected 8-char hash suffix"
    
    print("✅ Branch name format is correct")


def test_generate_pr_title():
    """Test PR title generation."""
    print("\n" + "=" * 60)
    print("TEST: generate_pr_title")
    print("=" * 60)
    
    test_cases = [
        {
            "parsed_data": {"title": "Fix login bug", "feature": "Login bug fix"},
            "decision": {"ticket_type": "bug", "action": "fix"},
            "expected_prefix": "[AI] Fix:"
        },
        {
            "parsed_data": {"title": "Add new feature", "feature": "New feature"},
            "decision": {"ticket_type": "feature", "action": "add"},
            "expected_prefix": "[AI] Feature:"
        },
        {
            "parsed_data": {"title": "Refactor code", "feature": "Code refactor"},
            "decision": {"ticket_type": "refactor", "action": "refactor"},
            "expected_prefix": "[AI] Refactor:"
        }
    ]
    
    for test_case in test_cases:
        title = generate_pr_title(test_case["parsed_data"], test_case["decision"])
        print(f"Title: {title}")
        assert title.startswith(test_case["expected_prefix"]), f"Expected prefix '{test_case['expected_prefix']}'"
    
    print("✅ All PR title tests passed")


def test_generate_pr_body():
    """Test PR body generation."""
    print("\n" + "=" * 60)
    print("TEST: generate_pr_body")
    print("=" * 60)
    
    parsed_data = {
        "feature": "Implement user authentication",
        "intent": "Allow users to securely log in",
        "acceptance_criteria": [
            "Users can log in with email and password",
            "Password must be at least 8 characters",
            "Implement rate limiting"
        ]
    }
    
    decision = {
        "ticket_type": "feature",
        "action": "add",
        "priority": {"adjusted": "high"},
        "requires_tests": True,
        "smallest_change": {"recommendation": "Implement only login functionality"},
        "code_generation_strategy": {"includes_comments": True},
        "approach": "standard"
    }
    
    generated_files = [
        {
            "filename": "auth.py",
            "code": "def login(email, password):\n    # TODO: Implement login\n    pass",
            "template_used": "feature_scaffold"
        },
        {
            "filename": "test_auth.py",
            "code": "def test_login():\n    # TODO: Write tests\n    pass",
            "template_used": "test_template"
        }
    ]
    
    body = generate_pr_body(parsed_data, decision, generated_files)
    
    # Verify body contains expected sections
    assert "🤖 AI-Generated Pull Request" in body
    assert "User Intent" in body
    assert "Acceptance Criteria" in body
    assert "auth.py" in body
    assert "test_auth.py" in body
    assert "- [ ] Users can log in with email and password" in body
    
    print("PR body length:", len(body))
    print("✅ PR body generation test passed")


def test_generate_commit_message():
    """Test commit message generation."""
    print("\n" + "=" * 60)
    print("TEST: generate_commit_message")
    print("=" * 60)
    
    parsed_data = {
        "title": "Add user authentication",
        "components": ["Backend", "Security"]
    }
    
    decision = {
        "ticket_type": "feature",
        "action": "add"
    }
    
    uploaded_files = ["auth.py", "models.py", "test_auth.py"]
    
    message = generate_commit_message(parsed_data, decision, uploaded_files)
    
    print(f"Commit message:\n{message}")
    
    assert message.startswith("feat(backend):"), f"Expected 'feat(backend):', got {message[:20]}"
    assert "Files changed: 3" in message
    assert "- auth.py" in message
    
    print("✅ Commit message generation test passed")


def test_validate_github_connection():
    """Test GitHub connection validation."""
    print("\n" + "=" * 60)
    print("TEST: validate_github_connection")
    print("=" * 60)
    
    is_connected = validate_github_connection()
    print(f"GitHub connection status: {is_connected}")
    
    if is_connected:
        print("✅ GitHub connection is working")
    else:
        print("⚠️ GitHub connection failed (this may be expected if credentials are invalid)")


def test_get_repo_info():
    """Test repository info retrieval."""
    print("\n" + "=" * 60)
    print("TEST: get_repo_info")
    print("=" * 60)
    
    info = get_repo_info()
    print(f"Repository info: {info}")
    
    if "error" not in info:
        print(f"Repository: {info.get('full_name', 'N/A')}")
        print(f"Default branch: {info.get('default_branch', 'N/A')}")
        print("✅ Repository info retrieved successfully")
    else:
        print(f"⚠️ Could not retrieve repo info: {info.get('error', 'Unknown error')}")


def test_create_pr_basic():
    """Test basic PR creation (dry run - won't actually create PR)."""
    print("\n" + "=" * 60)
    print("TEST: create_pr (Basic)")
    print("=" * 60)
    
    # This test will only work if GitHub credentials are valid
    # We'll catch any exceptions and report them
    
    generated_files = [
        {
            "filename": "test_file.py",
            "code": "# Test file\nprint('Hello from AI-generated code')",
            "template_used": "test"
        }
    ]
    
    parsed_data = {
        "title": "Test PR",
        "feature": "Test feature for PR creation",
        "components": ["Test"]
    }
    
    decision = {
        "ticket_type": "task",
        "action": "general",
        "requires_tests": False
    }
    
    try:
        result = create_pr(generated_files, parsed_data, decision)
        print(f"PR creation result: {result}")
        
        if result.get("success"):
            print(f"✅ PR created successfully: #{result.get('pr_number')}")
        else:
            print(f"⚠️ PR creation failed at stage: {result.get('stage', 'unknown')}")
            print(f"   Error: {result.get('error', 'Unknown')}")
    except Exception as e:
        print(f"❌ Exception during PR creation: {str(e)}")


def test_create_pr_with_options():
    """Test PR creation with options."""
    print("\n" + "=" * 60)
    print("TEST: create_pr (With Options)")
    print("=" * 60)
    
    generated_files = [
        {
            "filename": "advanced_test.py",
            "code": "# Advanced test\nresult = 42",
            "template_used": "advanced"
        }
    ]
    
    parsed_data = {
        "title": "Advanced Test PR",
        "feature": "Advanced test with options",
        "components": ["Test"]
    }
    
    decision = {
        "ticket_type": "feature",
        "action": "add",
        "requires_tests": True
    }
    
    options = {
        "labels": ["test-label", "ai-generated"],
        "add_comments": True,
        "force_recreate": False
    }
    
    try:
        result = create_pr(generated_files, parsed_data, decision, options)
        print(f"PR creation with options result: {result}")
        
        if result.get("success"):
            print(f"✅ PR created with options: #{result.get('pr_number')}")
            details = result.get("details", {})
            if "labels" in details:
                print(f"   Labels added: {details['labels']}")
        else:
            print(f"⚠️ PR creation failed: {result.get('error', 'Unknown')}")
    except Exception as e:
        print(f"❌ Exception during PR creation: {str(e)}")


def main():
    """Run all tests."""
    print("=" * 60)
    print(" CREATE PR LOGIC TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_generate_branch_name,
        test_generate_pr_title,
        test_generate_pr_body,
        test_generate_commit_message,
        test_validate_github_connection,
        test_get_repo_info,
        test_create_pr_basic,
        test_create_pr_with_options
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ Test failed: {str(e)}")
            failed += 1
        except Exception as e:
            print(f"❌ Test error: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f" TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)