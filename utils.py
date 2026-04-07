import re as _re
import json
import pandas as pd
import duckdb
from config import client
import streamlit as st


# -------------------------------
# FILE LOADER
# -------------------------------
@st.cache_data
def load_file(file_bytes: bytes, file_name: str):
    """
    Cache-aware file loader. Accepts raw bytes so Streamlit can hash the input.
    Re-parsing only happens when the uploaded file actually changes.
    """
    try:
        if file_name.endswith(".csv"):
            df = pd.read_csv(pd.io.common.BytesIO(file_bytes))
        else:
            df = pd.read_excel(pd.io.common.BytesIO(file_bytes))
        return df, df.columns.tolist()
    except Exception as e:
        return None, str(e)


# -------------------------------
# PROMPT BUILDER
# -------------------------------
def build_prompt(query: str, columns: list[str]) -> str:
    return f"""
You are an expert SQL optimizer.

Optimize the SQL query based ONLY on given column names.
Do not assume extra columns.
if user query is SELECT * then optimize query to SELECT column1, column2 from table return.
if user query is SELECT * then issue in write SELECT * is that it can lead to performance issues.
"already_optimal" must be true ONLY if no changes are needed.
Do NOT modify logic unnecessarily.
if you optimize query then same query resend then you return query is already optimal and return same query.
if original query is already optimal that without_optimize_query_time and with_optimize_query_time must be same and not return 0.
JSON into the not use ` for quoting column names because it can cause issues with parsing in some cases. Use double quotes " instead if needed.
if use column names that to be return same to same and not change column names because it can cause issues with parsing in some cases.

Return ONLY JSON:

{{
  "optimized_query": "",
  "issues": [],
  "explanation": [],
  "already_optimal": false,
  "without_optimize_query_time": int()ms,
  "with_optimize_query_time": int()ms
}}

SQL Query:
{query}

Columns:
{", ".join(columns)}
"""


# -------------------------------
# GROQ API CALL
# -------------------------------
def call_groq(prompt: str) -> dict:
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=0,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


# -------------------------------
# SQL HELPERS
# -------------------------------
def sanitize_sql(sql: str, columns: list = None) -> str:
    """
    1. Replace MySQL-style backtick identifiers with DuckDB double quotes.
    2. Auto-quote dataset column names that contain spaces or special chars
       (e.g. 'RAM (GB)') so DuckDB does not mistake them for function calls.
       Only replaces occurrences that are not already wrapped in double quotes.
    """
    # Step 1: backticks -> double quotes
    sql = sql.replace("`", '"')

    # Step 2: auto-quote problematic column names from the actual dataset
    if columns:
        for col in sorted(columns, key=len, reverse=True):
            if _re.search(r'[\s()\[\]]', col):
                if f'"{col}"' not in sql:
                    sql = _re.sub(_re.escape(col), f'"{col}"', sql, flags=_re.IGNORECASE)
    return sql


def run_query(con: duckdb.DuckDBPyConnection, sql: str, columns: list = None) -> pd.DataFrame:
    return con.execute(sanitize_sql(sql, columns)).fetchdf()


def display_sql(sql: str, columns: list = None) -> str:
    """
    Strip double quotes from column names for clean display only.
    Execution still uses sanitize_sql (with quotes) so DuckDB works correctly.
    """
    sql = sql.replace("`", "")
    if columns:
        for col in sorted(columns, key=len, reverse=True):
            sql = sql.replace(f'"{col}"', col)
    return sql
