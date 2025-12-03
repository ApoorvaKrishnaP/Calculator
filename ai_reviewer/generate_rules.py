import os
import json
import google.genai as genai
from google.genai import types
print("trial")
print("trial2")
print("trial3")
print("Trial3")
#my name is apoorva.my github username is apoorva.my gmail is apoorva@apoorva.com
#print("Todos")
#test comment
#test comment2#
def generate_rules(comments_file_path, output_rules_path):
    """
    Reads PR comments from a JSON file and uses Gemini to generate coding rules.
    """
    # 1. Security: Get API key from environment variable



    # 2. Setup: Use the Client pattern you prefer
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    if not os.path.exists(comments_file_path):
        print(f"No comments file found at {comments_file_path}")
        return

    # 3. Data Processing: Keep input as comments list
    with open(comments_file_path, 'r') as f:
        comments_data = json.load(f)
        # Extract just the body text, ignoring empty ones
        comments = [c['body'] for c in comments_data if c.get('body')]

    comments_text = "\n- ".join(comments)

    # Read existing rules to avoid duplicates
    existing_rules = ""
    if os.path.exists(output_rules_path):
        try:
            with open(output_rules_path, 'r') as f:
                existing_rules = f.read()
        except Exception as e:
            print(f"Warning: Could not read existing rules: {e}")

    prompt = f"""
    ROLE:
    You are a Senior Staff Engineer. Below is a list of code review comments made on our Pull Requests in the past.
    
    TASK:
    Analyze these comments and extract a set of clear, actionable coding rules and style guidelines for this project.
    
    GUIDELINES:
    1. **Filter Noise**: Ignore non-constructive comments like "great job", "looks good", "thanks", or general praise. Only focus on comments that suggest a change or best practice.
    2. **Avoid Duplicates**: Check the "EXISTING RULES" section below. Do NOT generate a rule if it is already covered by an existing rule.
    3. **Merge**: Output the COMPLETE set of rules (Existing + New valid rules). If a new rule conflicts with an existing one, use your judgment to refine it, but generally preserve established rules unless the new comment explicitly overrides them.
    4. **Format**: Output ONLY the rules as a numbered list in Markdown. No intro/outro.

    EXISTING RULES:
    {existing_rules}
    
    NEW COMMENTS:
    - {comments_text}
    
    FEW-SHOT EXAMPLES:
    
    Example 1:
    Input Comments:
    - "add only necessary comments"
    - "Great work on this function!"
    Output:
    **Minimize Comments**: Include only comments that are necessary for understanding the code's purpose or complex logic. Avoid redundant or obvious comments.

    Example 2:
    Input Comments:
    - "Ensure first letter is capitalized in print statements"
    Output:
    **Capitalize Print Statement Sentences**: All sentences within print statements should start with a capital letter. This includes the first word of the sentence and proper nouns.
    
    OUTPUT FORMAT:
    Output ONLY the rules. Do not include any conversational text, introductions, or conclusions.
    Format the output as a numbered list of rules in Markdown.
    """

    # 4. Execution: Use the new generate_content style
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        
        rules = response.text
        print(rules)
        with open(output_rules_path, 'w') as f:
            
            f.write(rules)
        
        print(f"Successfully generated rules to {output_rules_path}")
        
    except Exception as e:
        print(f"Error generating rules: {e}")

if __name__ == "__main__":
    generate_rules("review_logs.json", "ai_reviewer/project_rules.md")
    generate_rules("review_logs.json", "ai_reviewer/project_rules.md")