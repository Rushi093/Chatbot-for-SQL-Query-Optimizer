import json
import streamlit as st
from groq import Groq

client = Groq(api_key="API_KEY_HERE")  # ⚠️ Replace with your API key


def optimize_sql(user_query):
    prompt = f"""
You are an expert SQL optimizer.

Your task:
Analyze the given SQL query and return ONLY a valid raw JSON object.
Do NOT include markdown, backticks, explanations outside JSON, or extra text.
if user send SELECT c.column1, c.column2, ... this is optimal query and return original query and set already_optimal to true

STRICT RULES:
1. Do NOT assume column names. If unknown, use: SELECT column1, column2, ...
2. If the query is already optimal, return the ORIGINAL query.
3. If your optimized query is the SAME as the original, mark already_optimal = true.
4. Do NOT modify logic unnecessarily.
5. Output MUST be valid JSON only.

JSON FORMAT:
{{
  "optimized_query": "<optimized or original query>",
  "issues": ["issue1", "issue2"],
  "explanation": ["step1", "step2"],
  "already_optimal": true/false,
  "without_optimize_query_time": <number>,
  "with_optimize_query_time": <number>
}}

IMPORTANT:
- "already_optimal" must be true ONLY if no changes are needed.
- Query times should be estimated numbers (e.g., 120, 60).
- Keep explanations short and clear.
- if original query is already optimal that without_optimize_query_time and with_optimize_query_time must be same and not return 0.

SQL Query:
{user_query}
"""

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    content = completion.choices[0].message.content.strip()

    try:
        st.write(json.loads(content))
        return json.loads(content)
    except Exception:
        st.error("❌ Failed to parse response. Raw output below:")
        st.code(content)
        return None
