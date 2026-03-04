import google.generativeai as genai
import yaml
import uuid
from pathlib import Path

# ---------------- CONFIG ----------------
genai.configure(api_key="AIzaSyCYHxgYfXz9inb_xSBDCuUF_8XUA1eqBA8")
MODEL = "gemini-2.5-flash"
RULES_DIR = Path("rules")
RULES_DIR.mkdir(exist_ok=True)
# ---------------------------------------

PROMPT = """
You are a static analysis rule author.

Convert the following English coding rule into a VALID Semgrep YAML rule.

Output MUST follow this exact structure:
rules:
  - id: rule-id
    message: clear message
    severity: WARNING
    languages: [python]
    pattern: REGEX_OR_PATTERN

Rules:
- Language: Python
- Output must be valid Semgrep YAML
- No explanations, no markdown, no autofix
- Return ONLY the YAML, nothing else

English rule:
\"\"\"
{rule}
\"\"\"
"""


def english_to_semgrep(rule_text: str) -> str:
    model = genai.GenerativeModel(MODEL)
    response = model.generate_content(PROMPT.format(rule=rule_text))

    yaml_text = response.text.strip()
    if yaml_text.startswith("```"):
        # Remove opening backticks and language specifier
        yaml_text = yaml_text.split("\n", 1)[1]  # Skip first line (```yaml)
    if yaml_text.endswith("```"):
        # Remove closing backticks
        yaml_text = yaml_text.rsplit("\n", 1)[0]

    yaml_text = yaml_text.strip()
    # Validate YAML early (critical)
    parsed = yaml.safe_load(yaml_text)
    if "rules" not in parsed:
        raise ValueError("Invalid Semgrep YAML generated")

    return yaml_text


def save_rule(yaml_text: str):
    rule_id = f"rule-{uuid.uuid4().hex[:8]}"
    path = RULES_DIR / f"{rule_id}.yaml"
    path.write_text(yaml_text)
    print(f"✔ Saved {path}")


if __name__ == "__main__":
    english_rules = [
        "Always use the with statement when opening files.",
        "Avoid using print() in production code.",
        "Use enumerate() instead of range(len()).",
        "Use list comprehensions instead of appending in a loop.",
        "Use f-strings instead of percent or str.format formatting."
    ]

    for rule in english_rules:
        yaml_rule = english_to_semgrep(rule)
        save_rule(yaml_rule)
