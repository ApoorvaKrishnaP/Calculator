import os
import sys
import json
import google.genai as genai
from github import Github

# Configure Gemini

#My github api key="888cbcddd789"
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
    - "violation": description of the rule violated
    - "suggestion": text explanation of how to fix it
    - "fix_code": (optional) the exact code line(s) that should replace the violated line(s). Only provide this if it's a simple replacement.

    CODE DIFF:
    {diff_text}
    """

    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt,
        config={"response_mime_type": "application/json"}
    )
    
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

    # 6. Post comments to GitHub PR
    print("Posting review comments to GitHub...")
    try:
        commits = list(pr.get_commits())
        latest_commit = commits[-1]
    except Exception as e:
        print(f"Error getting commits: {e}")
        return review_comments

    for comment in review_comments:
        try:
            body = f"**AI Reviewer Found a Violation!**\n\n**Rule:** {comment['violation']}\n**Suggestion:** {comment['suggestion']}"
            
            # If the AI provided exact fix code, use GitHub's suggestion feature
            if "fix_code" in comment and comment["fix_code"]:
                body += f"\n```suggestion\n{comment['fix_code']}\n```"

            # Create a review comment on the specific line
            # Note: 'line' must be part of the diff for this to work
            pr.create_review_comment(
                body=body,
                commit=latest_commit,
                path=comment['file'],
                line=int(comment['line']),
                side="RIGHT"
            )
            print(f"Posted comment on {comment['file']}:{comment['line']}")
        except Exception as e:
            print(f"Failed to post comment on {comment['file']}:{comment['line']}: {e}")

    return review_comments

if __name__ == "__main__":
    # These would typically come from GitHub Actions context
    repo = os.environ["GITHUB_REPOSITORY"]
    pr_num = int(os.environ["PR_NUMBER"])
    print("Running AI Reviewer...")
    review_pr(repo, pr_num, "ai_reviewer/project_rules.md")
