import streamlit as st
from streamlit_ace import st_ace
from optimizer import optimize_sql
from ui import render_results

st.set_page_config(page_title="SQL Query Optimizer", layout="wide")

# st.set_page_config(layout="wide")

# ---------- HEADER ----------
st.markdown("""
    <h1 style='text-align: center;'>⚡ SQL Query Optimizer</h1>
""", unsafe_allow_html=True)

st.sidebar.success("select a page above.")

# ------------------ UI ------------------
# st.title("⚡ SQL Query Optimizer")

query = st_ace(
    placeholder="Write your SQL query here...",
    language="sql",
    theme="monokai",
    height=300,
    auto_update=True
)

optimize_btn = st.button("Optimize Query")

# ------------------ PROCESS ------------------
if optimize_btn and query.strip():
    with st.spinner("Optimizing..."):
        data = optimize_sql(query)

    if data:
        render_results(query, data)

elif optimize_btn:
    st.warning("Please enter a SQL query.")
