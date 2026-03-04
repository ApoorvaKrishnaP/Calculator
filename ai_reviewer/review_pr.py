import os
import json
from github import Github, GithubException
import litellm

g = Github(os.getenv("GITHUB_TOKEN"))
repo = g.get_repo(os.getenv("GITHUB_REPOSITORY"))
pr = repo.get_pull(int(os.getenv("GITHUB_PR_NUMBER")))  # GitHub Actions sets this? Wait — we will pass it

# Better: use event
event_path = os.getenv("GITHUB_EVENT_PATH")
with open(event_path) as f:
    event = json.load(f)
pr = repo.get_pull(event["pull_request"]["number"])

# 1. Get diff + rules
diff = pr.get_files()
rules = repo.get_contents("project_rules.md").decoded_content.decode()

# 2. Build prompt (critical part)
system_prompt = """You are an expert code reviewer. You have a rulebook.
Return ONLY valid JSON array of violations.
For each violation include:
- file (path)
- start_line (1-based in the NEW version of file)
- end_line
- start_column (only if violation is on single line, else null)
- end_column (only if single line)
- rule_id
- rule_name
- why (exact reason from rulebook)
- solution (clear fix explanation)
- suggested_code (the fixed code snippet)

Rules:
""" + rules

# 3. Call LLM with LiteLLM (cheap & any model)
violations = []
for file in diff:
    if file.status in ["added", "modified"]:
        hunk = file.patch or ""
        user_prompt = f"File: {file.filename}\nDiff:\n{hunk}\n\nAnalyze and return violations as JSON array."
        
        response = litellm.completion(
            model=os.getenv("LLM_MODEL"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        try:
            result = json.loads(response.choices[0].message.content)
            violations.extend(result.get("violations", []))
        except:
            pass  # skip bad response

# 4. Create Check Run with ANNOTATIONS (this is what shows in IDE)
annotations = []
for v in violations[:50]:  # max 50 per request
    ann = {
        "path": v["file"],
        "start_line": v["start_line"],
        "end_line": v.get("end_line", v["start_line"]),
        "annotation_level": "failure",
        "title": f"Rule {v['rule_id']}: {v['rule_name']}",
        "message": f"{v['why']}\n\nSolution: {v['solution']}",
        "raw_details": f"Suggested fix:\n{v.get('suggested_code', '')}"
    }
    if v.get("start_column") and v.get("end_column"):
        ann["start_column"] = v["start_column"]
        ann["end_column"] = v["end_column"]
    annotations.append(ann)

check_run = repo.create_check_run(
    name="RuleForge AI Review",
    head_sha=pr.head.sha,
    status="completed",
    conclusion="failure" if annotations else "success",
    output={
        "title": "RuleForge AI Code Review",
        "summary": f"Found {len(annotations)} rule violations.\n\nFull rulebook: project_rules.md",
        "annotations": annotations
    }
)

print(f"✅ Created check run with {len(annotations)} annotations")