import streamlit as st
import json
from groq import Groq
import sqlparse
from streamlit_ace import st_ace
import os


st.set_page_config(page_title="SQL Optimizer", layout="wide")

# client = Groq(api_key="GROQ_API_KEY_HERE")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))     # API KEY Insert Here -------------------------------------------

# ------------------ UI ------------------
st.title("⚡ SQL Query Optimizer")

# query = st.text_area("Enter your SQL Query:", height=200)

query = st_ace(
    placeholder="Write your SQL query here...",
    language="sql",
    theme="monokai",
    height=300,
    auto_update=True
)

optimize_btn = st.button("Optimize Query")

# ------------------ FUNCTION ---------------------------------
def optimize_sql(user_query):
#     prompt = f"""You are an expert SQL optimizer.
# Analyze the SQL query below and return ONLY a raw JSON object (no markdown, no backticks, no extra text).
# streetly you not assume column names, if need then SELECT * then return SELECT column 1, column 2, ... 
# if original query and opimize query is same then return original query and set already_optimal to true
# original query in not change then return that is allready optimal and set already_optimal to true
# if you opimize query is resend same as original query then return that is allready optimal and set already_optimal to true

# JSON format:
# {{
#   "optimized_query": "<improved SQL, or original if already optimal>",
#   "issues": ["<issue 1>", "<issue 2>"],
#   "explanation": ["<step 1>", "<step 2>"],
#   "already_optimal": true,
#   "without_optimize_query_time": 100,
#   "with_optimize_query_time": 50
# }}

# SQL Query:
# {user_query}
# """

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

    # Safe JSON parsing
    try:
        # st.write(json.loads(content))
        return json.loads(content)
    except:
        st.error("❌ Failed to parse response. Raw output below:")
        st.code(content)
        return None

# ------------------ PROCESS ------------------------------------
if optimize_btn and query.strip():
    with st.spinner("Optimizing..."):
        data = optimize_sql(query)

    if data:
        st.success("✅ Optimization Complete")

        # ------------------ METRICS -------------------
        original_time = data.get("without_optimize_query_time", 0)
        optimized_time = data.get("with_optimize_query_time", 0)

        improvement = 0
        if original_time > 0:
            improvement = ((original_time - optimized_time) / original_time) * 100

        col3, col4, col5 = st.columns(3)

        # col3.metric("Original Time (ms)", original_time)
        # col4.metric("Optimized Time (ms)", optimized_time)
        # col5.metric("Improvement %", f"{improvement:.2f}%")
        
        # Calculate improvement --------------------------
        improvement = 0
        if original_time > 0:
            improvement = ((original_time - optimized_time) / original_time) * 100

        col3, col4, col5 = st.columns(3)

        # Original -----------------------
        col3.metric(
            "⏱️ Original (ms)",
            f"{original_time:.2f} ms"
        )

        # Optimized -----------------------
        col4.metric(
            "⚡ Optimized (ms)",
            f"{optimized_time:.2f} ms"
        )

        # Improvement (custom format) -----------------------
        if improvement >= 0:
            col5.metric(
                "📈 Speed Improvement",
                f"{original_time - optimized_time:.2f} faster",
                f"+{improvement:.2f}%"
            )
        else:
            col5.metric(
                "📉 Speed Decrease",
                f"{abs(improvement):.2f}% slower",
                f"{improvement:.2f}%"
            )
            
        # ------------------ OUTPUT -------------------------------
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📄 Original Query")
            st.code(query, language="sql")

        with col2:
            st.subheader("⚡ Optimized Query")
            formatted_optimized = sqlparse.format(data.get("optimized_query", ""), reindent=True, keyword_case='upper')
            st.code(formatted_optimized, language="sql")

        # ------------------ STATUS ------------------------------
        if data.get("already_optimal"):
            st.info("✅ Query is already optimized")
        # else:
        #     st.warning("⚠️ Query was improved")

        # ------------------ ISSUES ------------------------------
        st.subheader("🚨 Issues Found")
        issues = data.get("issues", [])
        if issues:
            for i in issues:
                st.write(f"- {i}")
        else:
            st.write("No issues found")

        # ------------------ EXPLANATION ------------------
        st.subheader("🧠 Explanation")
        explanation = data.get("explanation", [])
        if explanation:
            for step in explanation:
                st.write(f"- {step}")
        else:
            st.write("No explanation provided")

# ------------------ EMPTY STATE ----------------------------------------------------
elif optimize_btn:
    st.warning("Please enter a SQL query.")
