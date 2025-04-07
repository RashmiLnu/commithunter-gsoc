import subprocess
import re

def get_commits(good_sha, bad_sha):
    """Get all commits between the good and bad versions."""
    # Using double quotes for Windows compatibility
    cmd = f'git log {good_sha}..{bad_sha} --pretty=format:"%H|%an|%ad|%s"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    commits = []
    for line in result.stdout.splitlines():
        parts = line.split('|', 3)
        if len(parts) >= 4:  # Ensure we have at least 4 parts
            commits.append({
                'sha': parts[0],
                'author': parts[1],
                'date': parts[2],
                'message': parts[3]
            })
    return commits

def get_changed_files(commit_sha):
    """Get list of files changed in a commit."""
    cmd = f"git show --name-only --pretty=format: {commit_sha}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return [line for line in result.stdout.splitlines() if line.strip()]

def score_commit(commit, test_name, failure_message):
    """Score a commit based on how likely it is to have caused the test failure."""
    score = 0
    message = commit['message'].lower()
    
    # Check for JFR-related terms in commit message
    if 'jfr' in message.lower():
        score += 10
    
    # Higher score for explicit monitor mentions
    if 'monitor enter' in message.lower() or 'monitorenter' in message.lower():
        score += 15
    
    # Check for terms related to the specific test failure
    if 'monitor' in message.lower():
        score += 8
    if 'thread' in message.lower():
        score += 5
    if 'event' in message.lower():
        score += 5
    
    # Check files changed
    files = get_changed_files(commit['sha'])
    
    # Look for JFR-related files
    jfr_files = [f for f in files if 'jfr' in f.lower()]
    
    # Higher score for JFR-related file changes
    score += len(jfr_files) * 3
    
    # Extra points for specific files that might affect JFR event recording
    for file in files:
        lower_file = file.lower()
        if 'chunk' in lower_file and 'writer' in lower_file:
            score += 5  # JFR chunk writer would handle event writing
        if 'event' in lower_file:
            score += 3
    
    return score, files

def find_problematic_commits(good_sha, bad_sha, test_name, failure_message):
    """Find commits that likely caused the test failure."""
    commits = get_commits(good_sha, bad_sha)
    results = []
    
    for commit in commits:
        score, files = score_commit(commit, test_name, failure_message)
        if score > 0:
            results.append({
                'sha': commit['sha'],
                'message': commit['message'],
                'score': score,
                'files': files
            })
    
    # Sort results by score (highest first)
    results.sort(key=lambda x: x['score'], reverse=True)
    return results

def main():
    # Our identified good and bad commits
    good_sha = "410fd54c52"  # v0.49.0-release HEAD
    bad_sha = "3baf4edc74"   # v0.51.0-release HEAD
    
    # The failing test information
    test_name = "jfr monitor enter"
    failure_message = "Required condition was not found: [Output match: jdk.JavaMonitorEnter]"
    
    print(f"Analyzing commits between {good_sha} and {bad_sha}")
    
    # First check if we can get any commits
    cmd = f'git log {good_sha}..{bad_sha} --pretty=format:"%H" --max-count=5'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if not result.stdout.strip():
        print("Error: No commits found between specified SHAs.")
        print("This could be because:")
        print("1. The SHAs are in the wrong order (good should be older than bad)")
        print("2. The SHAs are not in the same branch history")
        print("3. Git is not able to find the specified commits")
        return
    
    problematic_commits = find_problematic_commits(good_sha, bad_sha, test_name, failure_message)
    
    if not problematic_commits:
        print("No potentially problematic commits found with a score > 0.")
        return
    
    print(f"\nFound {len(problematic_commits)} potentially problematic commits.")
    print("\nTop potentially problematic commits:\n")
    for i, commit in enumerate(problematic_commits[:10]):  # Show top 10
        print(f"{i+1}. Score: {commit['score']}, SHA: {commit['sha'][:8]}")
        print(f"   Message: {commit['message']}")
        print(f"   Files changed: {len(commit['files'])}")
        jfr_files = [f for f in commit['files'] if 'jfr' in f.lower()]
        if jfr_files:
            print(f"   JFR-related files:")
            for file in jfr_files[:5]:  # Show up to 5 JFR-related files
                print(f"     - {file}")
        print()

if __name__ == "__main__":
    main()