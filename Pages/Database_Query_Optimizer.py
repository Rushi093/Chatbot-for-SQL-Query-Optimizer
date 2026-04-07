import streamlit as st
import duckdb
from streamlit_ace import st_ace

from config import setup_page
from utils import load_file, build_prompt, call_groq, run_query
from components import (
    render_data_preview,
    render_performance,
    render_queries,
    render_output_data,
    render_issues_and_explanation,
)


# -------------------------------------------------------------

st.set_page_config(layout="wide")

# ---------- HEADER ----------
st.markdown("""
    <h1 style='text-align: center;'>🗄️ Database Query Optimizer</h1>
    <p style='text-align: center; color: gray;'>
        Upload data → Write query → Analyze performance
    </p>
""", unsafe_allow_html=True)


# ---------- STEP BAR ----------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style='background-color:#87B6BC; padding:15px; border-radius:10px'>
        <b>Step 1</b><br>
        Upload CSV / Excel File
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='background-color:#87B6BC; padding:15px; border-radius:10px'>
        <b>Step 2</b><br>
        Write SQL Query
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style='background-color:#87B6BC; padding:15px; border-radius:10px'>
        <b>Step 3</b><br>
        View Results & Performance
    </div>
    """, unsafe_allow_html=True)


st.markdown("---")


# # ---------- MAIN LAYOUT ----------
# left, middle, right = st.columns([1,1,1])


# # ---------- STEP 1: FILE UPLOAD ----------
# with left:
#     st.subheader("Upload File")

#     uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

#     if uploaded_file:
#         if uploaded_file.name.endswith(".csv"):
#             df = pd.read_csv(uploaded_file)
#         else:
#             df = pd.read_excel(uploaded_file)

#         st.success("File uploaded successfully")

#         st.write("Preview:")
#         st.dataframe(df.head())


# # ---------- STEP 2: SQL QUERY ----------
# with middle:
#     st.subheader("Write SQL Query")

#     query = st.text_area("Enter SQL Query", height=200)

#     run = st.button("Run Query")


# # ---------- STEP 3: OUTPUT ----------
# with right:
#     st.subheader("Results & Insights")

#     if run:
#         st.write("### Query Performance")
#         st.metric("Execution Time", "120 ms")
#         st.metric("Rows Returned", "5")
#         st.metric("Rows Scanned", "10,000")

#         st.write("### Optimized Query")
#         st.code("SELECT customer, COUNT(*) FROM data GROUP BY customer")

#         st.write("### Issues")
#         st.warning("Full table scan detected")

#         st.write("### Explanation")
#         st.info("Query groups customers and counts total orders.")














# -------------------------------------------------

# -------------------------------
# CONFIG
# -------------------------------
setup_page("Database Query Optimizer")

# -------------------------------
# SESSION STATE
# -------------------------------
if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = False

# -------------------------------
# TITLE
# -------------------------------
# st.title("🗄️ Database Query Optimizer")

# -------------------------------
# STEP 1: FILE UPLOAD
# -------------------------------
st.subheader("📤 Upload Dataset")

uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    # with st.spinner("Running....."):
    df, columns = load_file(uploaded_file.read(), uploaded_file.name)

    if df is not None:
        st.session_state.file_uploaded = True
        st.session_state.df = df
        st.session_state.columns = columns

        st.success("File uploaded successfully")
        render_data_preview(df)
    else:
        st.error(columns)  # `columns` holds the error string on failure

# -------------------------------
# STEP 2: SQL INPUT
# -------------------------------
if st.session_state.file_uploaded:

    st.subheader("⚡ Enter SQL Query")

    query = st_ace(
        placeholder="Write your SQL query here...",
        language="sql",
        theme="monokai",
        height=300,
        auto_update=True,
    )

    run_btn = st.button("Run Optimization")

    if run_btn:
        if not query.strip():
            st.error("Please enter SQL query")
            st.stop()

        with st.spinner("Optimizing query..."):
            try:
                data = call_groq(build_prompt(query, st.session_state.columns))
                st.write(data)  # retained: matches original debug output
            except Exception as e:
                st.error(f"Groq API Error: {e}")
                st.stop()

        # -------------------------------
        # SQL EXECUTION (DuckDB)
        # -------------------------------
        con = duckdb.connect()
        con.register("data_table", st.session_state.df)

        try:
            original_df = run_query(con, query, st.session_state.columns)
            original_time = data.get("without_optimize_query_time", 0)
        except Exception as e:
            st.error(f"Original Query Error: {e}")
            con.close()
            st.stop()

        optimized_query = data.get("optimized_query", query)

        try:
            optimized_df = run_query(con, optimized_query, st.session_state.columns)
            optimized_time = data.get("with_optimize_query_time", 0)
        except Exception as e:
            st.error(f"Optimized Query Error: {e}")
            con.close()
            st.stop()

        con.close()  # always release the in-memory connection

        # -------------------------------
        # RENDER RESULTS
        # -------------------------------
        render_performance(original_time, optimized_time)
        render_queries(query, optimized_query, st.session_state.columns)
        render_output_data(optimized_df)
        render_issues_and_explanation(data)
