import os
import sys
import json
import google.genai as genai
from github import Github

# Configure Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def review_pr(repo_name, pr_number, rules_path):
    # 1. Setup GitHub connection
    g = Github(os.environ.get("GITHUB_TOKEN"))
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    # 2. Get the Diff
    # We use requests or the internal URL to get the raw diff, or iterate through files
    # For simplicity, let's iterate through files to get context
    files = pr.get_files()
    diff_text = ""
    for file in files:
        if file.status == "removed":
            continue
        diff_text += f"\n--- File: {file.filename} ---\n"
        diff_text += file.patch if file.patch else "(Binary file or too large)"

    # 3. Read Rules
    if not os.path.exists(rules_path):
        print("No rules file found. Skipping AI review.")
        return

    with open(rules_path, 'r') as f:
        rules = f.read()

    # 4. Ask Gemini to Review
    prompt = f"""
    You are an AI Code Reviewer. 
    Your goal is to enforce the following PROJECT RULES strictly.
    
    PROJECT RULES:
    {rules}

    INSTRUCTIONS:
    Review the code diff below. 
    If you find any code that violates the Project Rules, report it.
    If the code is fine, say "No violations found."
    
    Format your response as a JSON list of objects, where each object has:
    - "file": filename
    - "line": line number (approximate, based on the diff)
    - "violation": description of the rule violated
    - "suggestion": how to fix it

    CODE DIFF:
    {diff_text}
    """

    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
    
    try:
        response_text=response.text
        response_text=response_text.lstrip("```json").rstrip("```")
        review_comments = json.loads(response_text)
    except Exception as e:
        print("Failed to parse JSON response from AI:", response.text)
        return

    # 5. Save results to summary.json
    with open("summary.json", "w") as f:
        json.dump(review_comments, f, indent=2)
    print("Saved review summary to summary.json")

    return review_comments

if __name__ == "__main__":
    # These would typically come from GitHub Actions context
    repo = os.environ["GITHUB_REPOSITORY"]
    pr_num = int(os.environ["PR_NUMBER"])
    print("Running AI Reviewer...")
    review_pr(repo, pr_num, "ai_reviewer/project_rules.md")
