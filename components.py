import streamlit as st
import sqlparse
from utils import sanitize_sql, display_sql


# -------------------------------
# DISPLAY HELPERS
# -------------------------------
def display_issues_or_explanation(items: list, fallback: str):
    if items:
        for item in items:
            st.write(f"- {item}")
    else:
        st.write(fallback)


def render_performance(original_time: float, optimized_time: float):
    st.subheader("📈 Performance")

    time_diff = original_time - optimized_time
    improvement = (time_diff / original_time * 100) if original_time > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("⏱ Original (ms)", f"{original_time:.2f} ms")
    col2.metric("⚡ Optimized (ms)", f"{optimized_time:.2f} ms")
    col3.metric(
        "📈 Speed Improvement",
        f"{time_diff:.2f} faster",
        delta=f"{improvement:.2f}%",
        delta_color="normal",
    )


def render_queries(query: str, optimized_query: str, columns: list):
    fmt = lambda q: sqlparse.format(
        display_sql(sanitize_sql(q, columns), columns),
        reindent=True,
        keyword_case="upper",
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📝 Original Query")
        st.code(fmt(query), language="sql")

    with col2:
        st.markdown("### 🚀 Optimized Query")
        st.code(fmt(optimized_query), language="sql")


def render_data_preview(df):
    st.subheader("📊 Data Preview")
    st.dataframe(df.head(10), use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.info("File Name: data_table")
    col2.info(f"Rows: {len(df)}")
    col3.info(f"Columns: {len(df.columns)}")


def render_output_data(df):
    st.subheader("📊 Output Data (Optimized Query Result)")
    st.dataframe(df, use_container_width=True)


def render_issues_and_explanation(data: dict):
    st.subheader("⚠️ Issues")
    display_issues_or_explanation(data.get("issues", []), "No issues found")

    st.subheader("📘 Explanation")
    display_issues_or_explanation(data.get("explanation", []), "No explanation provided")
