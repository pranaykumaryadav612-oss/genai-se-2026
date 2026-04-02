# Create PR Logic - Comprehensive Documentation

## Overview

The `create_pr` function in `jira_ai_engine/github_pr.py` handles the complete workflow of creating a GitHub Pull Request from AI-generated code. This document explains the enhanced implementation with atomic commits, robust error handling, and configurable options.

## Key Features

### 1. **Atomic Commits**
- All files are committed together in a single atomic operation
- Ensures consistency - either all files are committed or none
- More efficient than individual file uploads

### 2. **Smart Branch Management**
- Generates meaningful branch names: `ai/{ticket-type}/{description}-{timestamp_hash}`
- Checks for existing branches to avoid conflicts
- Optional force recreation of existing branches

### 3. **Comprehensive Error Handling**
- Detailed error messages at each stage
- Fallback mechanisms (e.g., base branch fallback: configured → main → master → develop)
- Graceful degradation (atomic commit → individual uploads if needed)

### 4. **Configurable Options**
- Custom labels
- Reviewer assignment
- Milestone assignment
- PR comments
- Force branch recreation

### 5. **Duplicate Prevention**
- Checks for existing PRs before creating new ones
- Validates file names (no path traversal)
- Skips invalid files

## Function Signature

```python
def create_pr(
    generated_files: List[Dict[str, Any]], 
    parsed_data: Dict[str, Any], 
    decision: Dict[str, Any],
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
```

### Parameters

- **generated_files**: List of file dictionaries with `filename` and `code`
- **parsed_data**: Parsed Jira ticket data
- **decision**: AI decision object with ticket type, action, etc.
- **options**: Optional configuration dictionary

### Options Dictionary

```python
options = {
    "labels": ["bug", "urgent"],           # Additional labels
    "reviewers": ["user1", "user2"],       # Users to request reviews from
    "milestone": 1,                        # Milestone number
    "add_comments": True,                  # Add AI generation notes
    "force_recreate": False                # Delete and recreate existing branch
}
```

## Execution Stages

The function tracks progress through these stages:

1. **validation**: Validate input files
2. **github_connection**: Connect to GitHub
3. **get_base_branch**: Find base branch
4. **generate_branch_name**: Create branch name
5. **create_branch**: Create new branch
6. **prepare_files**: Validate and prepare files
7. **create_commit**: Create atomic commit
8. **check_existing_pr**: Check for duplicate PRs
9. **generate_pr_content**: Create title and description
10. **create_pr**: Create the pull request
11. **add_labels**: Add labels to PR
12. **add_reviewers**: Request reviews
13. **add_comments**: Add PR comments

## Return Value

```python
{
    "success": True,
    "pr_number": 42,
    "pr_url": "https://github.com/...",
    "branch": "ai/feature/user-auth-abc123",
    "title": "[AI] Feature: Implement user authentication",
    "stage": "complete",
    "details": {
        "repo": "owner/repo",
        "base_branch": "main",
        "base_sha": "abc123...",
        "branch_name": "ai/feature/user-auth-abc123",
        "files_uploaded": ["auth.py", "test_auth.py"],
        "files_skipped": [],
        "commit_sha": "def456...",
        "labels": ["ai-generated", "feature"],
        "reviewers": {"requested": ["user1"], "failed": []}
    }
}
```

## Helper Functions

### `generate_branch_name(parsed_data, decision)`
Creates a unique branch name with timestamp hash to avoid conflicts.

### `generate_pr_title(parsed_data, decision)`
Creates a descriptive PR title with [AI] prefix and action type.

### `generate_pr_body(parsed_data, decision, generated_files)`
Generates comprehensive PR description with:
- Summary and metadata
- File previews
- Acceptance criteria
- Testing checklist
- AI generation notes

### `generate_commit_message(parsed_data, decision, uploaded_files)`
Creates conventional commit-style messages (feat/fix/refactor/chore).

### `create_atomic_commit(repo, branch_name, base_sha, files)`
Creates a single commit with all files using GitHub's low-level API.

### `check_existing_pr(repo, branch_name, base_branch)`
Checks if a PR already exists for this branch.

### `add_pr_reviewers(pr, reviewers)`
Requests reviews from specified users.

### `add_pr_comments(pr, files_to_change, decision)`
Adds AI generation notes as a PR comment.

## Usage Examples

### Basic Usage

```python
from jira_ai_engine.github_pr import create_pr

result = create_pr(
    generated_files=[
        {"filename": "main.py", "code": "print('Hello')"},
        {"filename": "test_main.py", "code": "def test_hello(): ..."}
    ],
    parsed_data={
        "title": "Add hello world",
        "feature": "Implement hello world functionality",
        "components": ["Core"]
    },
    decision={
        "ticket_type": "feature",
        "action": "add",
        "requires_tests": True
    }
)
```

### Advanced Usage with Options

```python
result = create_pr(
    generated_files=files,
    parsed_data=parsed_data,
    decision=decision,
    options={
        "labels": ["ai-generated", "backend", "priority:high"],
        "reviewers": ["tech-lead", "qa-team"],
        "milestone": 3,
        "add_comments": True,
        "force_recreate": False
    }
)

if result["success"]:
    print(f"PR created: #{result['pr_number']}")
    print(f"URL: {result['pr_url']}")
else:
    print(f"Failed at stage: {result['stage']}")
    print(f"Error: {result.get('error', 'Unknown')}")
```

## Error Handling

The function handles various error scenarios:

### GitHub API Errors
- Invalid credentials
- Repository not found
- Permission issues
- Rate limiting

### Validation Errors
- No files provided
- Invalid file names (path traversal)
- Missing file content

### Branch Errors
- Branch already exists
- Cannot create branch
- Base branch not found

### PR Creation Errors
- No commits between branches
- PR already exists
- Invalid base branch

## Best Practices

1. **Always check the return value** - Don't assume success
2. **Use options for customization** - Leverage labels, reviewers, etc.
3. **Handle errors gracefully** - Check the `stage` and `error` fields
4. **Validate inputs** - Ensure files have valid names and content
5. **Consider dry runs** - Test with `dry_run=True` in main pipeline first

## Integration with Main Pipeline

The `create_pr` function is called from `main.py` as part of the complete pipeline:

```python
# Stage 4: Create PR
pr_result = create_pr(generated_files, parsed_data, decision)

if pr_result.get("success"):
    print(f"✅ PR Created: #{pr_result['pr_number']}")
    print(f"   URL: {pr_result['pr_url']}")
else:
    print(f"❌ PR Creation Failed: {pr_result.get('error', 'Unknown')}")
```

## Security Considerations

1. **File name validation** - Prevents path traversal attacks
2. **Content validation** - Ensures files are not empty
3. **Token security** - Uses environment variables for GitHub token
4. **Error message sanitization** - Doesn't expose sensitive information

## Performance Optimizations

1. **Atomic commits** - Single API call for all files
2. **Batch operations** - Labels, reviewers added together
3. **Early validation** - Fails fast on invalid inputs
4. **Smart fallbacks** - Graceful degradation on errors

## Future Enhancements

Potential improvements:
- Support for multiple commits (one per file type)
- Automatic conflict resolution
- Smart reviewer assignment based on file changes
- PR template support
- Automated testing integration
- Rollback capabilities

## Troubleshooting

### Common Issues

**Issue**: "No commits between branches"
- **Cause**: Generated files are identical to existing files
- **Solution**: Modify files or use `force_recreate` option

**Issue**: "Reference already exists"
- **Cause**: Branch name collision
- **Solution**: Use unique branch names or `force_recreate`

**Issue**: "Could not find a valid base branch"
- **Cause**: Configured base branch doesn't exist
- **Solution**: Check `.env` file or ensure branch exists

**Issue**: "No files were uploaded"
- **Cause**: All files failed validation
- **Solution**: Check file names and content

## Testing

Test the create PR logic with:

```bash
# Dry run (no actual PR created)
python test_pipeline.py

# With actual PR creation (requires valid GitHub token)
python -c "from jira_ai_engine import run_pipeline; run_pipeline('Your ticket text', dry_run=False)"
```

## Conclusion

The enhanced `create_pr` function provides a robust, feature-rich implementation for automated PR creation. It handles edge cases, provides detailed feedback, and integrates seamlessly with the Jira AI Engine pipeline.