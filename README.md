# CommitHunter Prototype - GSOC 2025

This repository contains my prototype implementation for Phase 1 of the CommitHunter project, created as part of my GSOC 2025 application for the Eclipse OpenJ9 project.

## Project Overview

CommitHunter is a tool designed to automatically identify problematic Git commits that cause test failures. This prototype demonstrates the rule-based approach (Phase 1) described in the project proposal.

## What This Prototype Does

The prototype uses a weighted scoring system to analyze commits between known "good" and "bad" build points, identifying which changes most likely caused a test failure. The implementation:

1. Analyzes all commits between specified good and bad SHAs
2. Scores each commit based on its relevance to the test failure
3. Ranks commits by their scores to identify likely culprits

## Example Use Case

This prototype was tested against a real OpenJ9 test failure case where JFR JavaMonitorEnter events were missing from test output. The script successfully identified two highly relevant commits:

1. "Fix owner for JFR monitor enter" (b73f5902)
2. "Add JFR monitor enter event" (629b382f)

## How to Run the Prototype

1. Clone this repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/REPO_NAME.git
   cd REPO_NAME
   ```

2. Set up a Python environment:
   ```bash
   # Create a virtual environment
   python -m venv venv

   # Activate the virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Run the script with the OpenJ9 repository:
   ```bash
   # First, clone the OpenJ9 repository if you don't have it
   git clone https://github.com/eclipse-openj9/openj9.git
   
   # Copy commit_hunter.py to the OpenJ9 directory
   cp commit_hunter.py openj9/
   
   # Run the script from within the OpenJ9 repository
   cd openj9
   python commit_hunter.py
   ```

## Code Explanation

The main components of the code are:

### 1. Commit Retrieval
```python
def get_commits(good_sha, bad_sha):
    """Get all commits between the good and bad versions."""
    cmd = f'git log {good_sha}..{bad_sha} --pretty=format:"%H|%an|%ad|%s"'
    # ...retrieves commit data from git
```

### 2. Scoring Algorithm
```python
def score_commit(commit, test_name, failure_message):
    """Score a commit based on how likely it is to have caused the test failure."""
    score = 0
    message = commit['message'].lower()
    
    # Various scoring rules based on commit message content
    if 'jfr' in message.lower():
        score += 10
    # ...more scoring rules
    
    # File change analysis
    files = get_changed_files(commit['sha'])
    jfr_files = [f for f in files if 'jfr' in f.lower()]
    score += len(jfr_files) * 3
    # ...additional file analysis
```

### 3. Result Ranking and Display
```python
# Sort results by score (highest first)
results.sort(key=lambda x: x['score'], reverse=True)
# ...display top results
```

## Future Plans

This prototype demonstrates the first phase of the CommitHunter project. In later phases, I plan to:

1. Implement machine learning models (like BERT/RoBERTa) to improve accuracy
2. Create automation for CI/CD integration
3. Build a visualization dashboard for tracking problematic commits

## GSOC Application

This repository is part of my application for the "CommitHunter: AI-Powered Commit Debugger" GSOC 2025 project with Eclipse OpenJ9.

For questions or feedback, please reach out through the GSOC application channels.
