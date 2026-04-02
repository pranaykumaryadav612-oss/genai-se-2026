# Jira AI Engine

**Jira → Code → PR**

An AI-powered engine that transforms Jira tickets into implementation code and automatically creates GitHub pull requests.

## Core Philosophy

- **"Jira → Code → PR"** - End-to-end automation
- **"Reduce manual engineering work"** - Focus on what matters
- **"From requirement to implementation"** - Bridge the gap

## Features

### 🔹 Input Understanding
- **Unstructured → Structured Data** - Parse raw Jira tickets into actionable JSON
- **Extract Intent from Text** - Understand what the user actually wants
- **Acceptance Criteria Parsing** - Identify test cases and validation steps

### 🔹 Decision Layer
- **Ticket Classification** - Automatically identify bug/feature/refactor/task
- **File Selection** - Determine what files should change
- **Smallest Change Analysis** - Find the minimal viable implementation

### 🔹 Code Generation
- **Scaffold, not full solution** - Generate starter templates for iteration
- **Template-based Generation** - Use proven patterns for consistency
- **Reusable Patterns** - Apply best practices automatically

### 🔹 PR Creation
- **Automated Branch Creation** - Smart branch naming conventions
- **Comprehensive PR Descriptions** - Include all relevant context
- **Label Management** - Auto-tag PRs by type

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Jira Ticket   │───▶│  Parser Module   │───▶│ Decision Module │───▶│ Generator Module│
│  (Raw Text)     │    │ (Unstructured →  │    │ (Classification │    │ (Code Creation) │
│                 │    │  Structured)     │    │  & Strategy)    │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘    └─────────────────┘
                                                                          │
                                                                          ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  GitHub PR      │◀───│  GitHub PR Module│◀───│ Generated Files │
│  (Created)      │    │  (Automation)    │    │  (Code + Tests) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd jira-ai-engine

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys
```

## Configuration

Set up your `.env` file with the following variables:

```env
# Groq API (for AI model)
GROQ_API_KEY=your_groq_api_key
MODEL_NAME=llama-3.3-70b-versatile

# GitHub (for PR creation)
GITHUB_TOKEN=your_github_token
REPO_NAME=owner/repo-name
BASE_BRANCH=main
```

## Usage

### Interactive Mode

```bash
python -m jira_ai_engine
```

### Command Line Mode

```bash
python -m jira_ai_engine "Your Jira ticket text here..."
```

### Programmatic Usage

```python
from jira_ai_engine import run_pipeline

# Define your ticket
ticket = """
As a user, I want to add a search feature to the product catalog.

Acceptance Criteria:
- Search by product name
- Filter by category
- Sort by price
- Display results in grid view
"""

# Run the pipeline
results = run_pipeline(ticket, project_context="E-commerce platform built with Python/Django")
```

### Dry Run Mode

Test the pipeline without creating actual PRs:

```python
results = run_pipeline(ticket, dry_run=True)
```

## Pipeline Stages

### Stage 1: Parsing (Input Understanding)

The parser converts unstructured Jira text into structured data:

```json
{
  "type": "feature",
  "title": "Add product search feature",
  "feature": "Implement search functionality for product catalog",
  "intent": "Allow users to find products quickly",
  "components": ["search", "catalog", "frontend"],
  "files_to_change": ["src/search/controller.py", "src/catalog/models.py"],
  "acceptance_criteria": ["Search by name", "Filter by category"],
  "priority": "high",
  "complexity": "medium"
}
```

### Stage 2: Decision Making

The decision engine analyzes the parsed data:

- **Ticket Type**: bug / feature / refactor / task
- **Action**: fix / add / refactor / general
- **Approach**: minimal_change / scaffold_first / incremental / standard
- **Files to Change**: Prioritized list with confidence scores
- **Smallest Change**: Recommendation for minimal implementation

### Stage 3: Code Generation

Based on the decision, the generator:

- Selects appropriate templates (bug_fix, feature_scaffold, api_endpoint, etc.)
- Generates code following the "scaffold first" philosophy
- Creates tests when required
- Returns structured file information

### Stage 4: PR Creation

The GitHub module:

- Creates a feature branch with meaningful name
- Uploads generated files
- Creates a comprehensive PR description
- Adds relevant labels

## Code Generation Templates

The engine includes templates for common scenarios:

- **Bug Fix**: Complete fix with regression tests
- **Feature Scaffold**: Starter template with TODO sections
- **API Endpoint**: FastAPI route structure
- **Database Model**: SQLAlchemy model template
- **Refactoring**: Safe incremental changes

## Examples

### Example 1: Bug Fix

**Input:**
```
Bug: User login fails when password contains special characters

Steps to reproduce:
1. Go to login page
2. Enter email and password with special chars (!@#$)
3. Click login
4. Get 500 error

Expected: Should login successfully
```

**Output:**
- Type: bug
- Action: fix
- Approach: minimal_change
- Generates: Fix + regression test
- Creates: PR with bug label

### Example 2: Feature Request

**Input:**
```
As a product manager, I want to export sales reports to CSV.

Acceptance Criteria:
- Export last 30 days by default
- Include all order details
- Download as CSV file
- Handle large datasets (10k+ rows)
```

**Output:**
- Type: feature
- Action: add
- Approach: scaffold_first
- Generates: API endpoint + model scaffold
- Creates: PR with feature label

## Best Practices

1. **Review Generated Code**: AI-generated code should always be reviewed
2. **Start Small**: The engine focuses on minimal changes
3. **Iterate**: Use scaffold code as a starting point
4. **Test Thoroughly**: Always run tests before merging
5. **Provide Context**: More project context = better results

## Limitations

- **AI Hallucinations**: May generate incorrect code
- **Context Limits**: Large codebases may need manual guidance
- **Complex Logic**: Business logic often requires human input
- **Testing**: Generated tests may need refinement

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [Create an issue]
- Documentation: [View docs]

---

*Built with ❤️ using Groq API and PyGithub*