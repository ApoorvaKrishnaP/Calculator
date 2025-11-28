import json
import sys
import subprocess
# check_reviews.py (Partial Code)
# Map human keywords to the executable tool or pattern.
TOOL_MAPPING = {
    "naming": "flake8",          # If naming mentioned, run flake8.
    "documentation": "pydocstyle", # If doc mentioned, run pydocstyle.
    "print": "print(",         # If print mentioned, search for literal "print(".
    "log": "print(",           # If logging mentioned, search for literal "print(".
    "imports": "flake8:import-errors",
    "capitalized": "regex:print-caps",
    "comments": "pylint:comment-density"
}
# check_reviews.py (Partial Code)
def get_required_checks(log_file):
    """Reads log and returns a set of required tools and patterns."""
    required_checks = set()
    try:
        with open(log_file, 'r') as f:
            review_data = json.load(f)
    except FileNotFoundError:
        return required_checks

    for comment in review_data:
        comment_body = comment['body'].lower()
        
        for keyword, rule_target in TOOL_MAPPING.items():
            if keyword in comment_body:
                # Add the required tool or pattern to the set
                required_checks.add(rule_target)
    
    return required_checks
# check_reviews.py (Partial Code)
def run_codified_checks(required_checks):
    """Executes external linters or internal string searches."""
    
    if "flake8" in required_checks:
        print("Running Naming/Style Check (flake8)...")
        # subprocess.run executes a command and waits for its exit code
        # If flake8 finds issues, it returns a non-zero code, which is an exception
        try:
            subprocess.run(["flake8", "."], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"::error file=ReviewRule::FLAKE8 check failed due to past style requirements.")
            print(e.stdout.decode())
            sys.exit(1)

    if "print(" in required_checks:
        print("Running Forbidden Pattern Check (print)...")
        # Check all files for the literal string "print("
        # You can use a more advanced regex check here if needed
        # For simplicity, we'll use a shell command via subprocess
        try:
            subprocess.run(f"grep -r 'print(' .", shell=True, check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print(f"::error file=ReviewRule::Forbidden 'print(' statement detected due to past logging rules.")
            sys.exit(1)
            
    # Add logic for pydocstyle, black, etc., here...
    
    print("SUCCESS: All required review rules passed.")