import streamlit as st
import sqlparse


def render_metrics(data):
    original_time = data.get("without_optimize_query_time", 0)
    optimized_time = data.get("with_optimize_query_time", 0)

    improvement = 0
    if original_time > 0:
        improvement = ((original_time - optimized_time) / original_time) * 100

    col3, col4, col5 = st.columns(3)

    col3.metric(
        "⏱️ Original (ms)",
        f"{original_time:.2f} ms"
    )

    col4.metric(
        "⚡ Optimized (ms)",
        f"{optimized_time:.2f} ms"
    )

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


def render_queries(original_query, optimized_query):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📄 Original Query")
        st.code(original_query, language="sql")

    with col2:
        st.subheader("⚡ Optimized Query")
        formatted_optimized = sqlparse.format(optimized_query, reindent=True, keyword_case='upper')
        st.code(formatted_optimized, language="sql")


def render_status(data):
    if data.get("already_optimal"):
        st.info("✅ Query is already optimized")


def render_issues(data):
    st.subheader("🚨 Issues Found")
    issues = data.get("issues", [])
    if issues:
        for i in issues:
            st.write(f"- {i}")
    else:
        st.write("No issues found")


def render_explanation(data):
    st.subheader("🧠 Explanation")
    explanation = data.get("explanation", [])
    if explanation:
        for step in explanation:
            st.write(f"- {step}")
    else:
        st.write("No explanation provided")


def render_results(query, data):
    st.success("✅ Optimization Complete")
    render_metrics(data)
    render_queries(query, data.get("optimized_query", ""))
    render_status(data)
    render_issues(data)
    render_explanation(data)
