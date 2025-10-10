import os
import json
from openai import OpenAI

# Initialize API client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load controls from repo (you can modify this to read YAML, Markdown, etc.)
controls_dir = "Controls"
results = []

prompt = """
You are SOC 2 Reviewer GPT, an AI auditor specializing in SOC 2 Type I and II.
Evaluate the provided control against AICPA Trust Services Criteria.
Return a structured JSON response with:
- control_id
- description
- mapped_tsc
- assessment_strengths
- assessment_weaknesses
- assessment_gaps
- recommendations
- readiness_rating
"""

for filename in os.listdir(controls_dir):
    if filename.endswith(".txt") or filename.endswith(".md") or filename.endswith(".yml"):
        with open(os.path.join(controls_dir, filename), "r") as file:
            control_text = file.read()

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": control_text}
            ],
            temperature=0.2
        )

        content = response.choices[0].message.content
        try:
            review = json.loads(content)
        except json.JSONDecodeError:
            review = {"error": "Invalid JSON returned", "raw_output": content}

        review["source_file"] = filename
        results.append(review)

# Save results
os.makedirs("Reports", exist_ok=True)
with open("Reports/soc2_review_results.json", "w") as out:
    json.dump(results, out, indent=2)

print("SOC 2 review complete. Results saved to Reports/soc2_review_results.json")
