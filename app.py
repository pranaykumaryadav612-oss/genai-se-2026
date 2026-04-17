Below is a production-ready Python code that utilizes a bug tracking system to store bug information. This example utilizes object-oriented principles and incorporates documentation to provide clarity.

```python
# Import required python modules
import json
import logging

# Set up logging configuration
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

class BugTracker:
    """
    A class to manage bug tracking.

    Attributes:
    -----------
    type (str): Type of the bug.
    goal (str): Goal to achieve by fixing the bug.
    files (list): List of files related to the bug.
    logic (str): Logic to fix the bug.
    acceptance_criteria (list): List of acceptance criteria for the bug.
    """

    def __init__(self, data):
        """
        Initialize BugTracker instance.

        Parameters:
        ----------
        data (dict): Input data.
        """
        self.type = data['type']
        self.goal = data['goal']
        self.files = data['files']
        self.logic = data['logic']
        self.acceptance_criteria = data['acceptance_criteria']

    def __str__(self):
        """
        Return a string representation of the bug.

        Returns:
        -------
        str: String representation of the bug.
        """
        return (
            f"Bug Type: {self.type}\n"
            f"Goal: {self.goal}\n"
            f"Affected Files: {self.files}\n"
            f"Logic: {self.logic}\n"
            f"Acceptance Criteria:\n"
            + "\n".join(self.acceptance_criteria)
        )

def parse_bug_data(data):
    """
    Parse bug data into a BugTracker instance.

    Parameters:
    ----------
    data (dict): Bug data.

    Returns:
    -------
    BugTracker: BugTracker instance.
    """
    try:
        bug = BugTracker(data)
        return bug
    except KeyError as e:
        logging.error(f"Missing key in data: {e}")
        return None

def load_bug_from_json(file_path):
    """
    Load bug from a JSON file.

    Parameters:
    ----------
    file_path (str): Path to the JSON file.

    Returns:
    -------
    BugTracker: BugTracker instance or None if the file is not found.
    """
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return parse_bug_data(data)
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in file: {file_path}")
        return None

# Example usage
if __name__ == "__main__":
    data = {
        "type": "bug",
        "goal": "Allow users to login after password reset",
        "files": ["passwordResetService.py", "sessionManager.py", "tokenManager.py"],
        "logic": "Fix reset password flow to update session and ensure proper token refresh.",
        "acceptance_criteria": [
            "User should be able to login successfully after password reset",
            "Session should be updated after password reset",
            "Token should refresh properly after password reset"
        ]
    }
    bug_tracker = parse_bug_data(data)
    if bug_tracker:
        print(bug_tracker)
    else:
        logging.error("Failed to parse bug data.")
```

In this example code, the `BugTracker` class encapsulates the bug-related attributes and methods. The `parse_bug_data` function is used to create a `BugTracker` instance from a dictionary. The `load_bug_from_json` function loads a bug from a JSON file and returns a `BugTracker` instance. 

This example follows the best practices for code readability, organization, and documentation. You can easily extend this code to fit your specific requirements and use cases.

To run this code, save it in a file, create a JSON file named `bug.json` with the provided input data, and use the `load_bug_from_json` function to load the bug.

```bash
python bug_tracker.py
```

Replace `bug_tracker.py` with the name of your Python file. The code uses the `logging` module for logging errors and other messages. You can adjust the logging level and format as needed.