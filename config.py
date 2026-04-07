import streamlit as st
from groq import Groq
import os

# -------------------------------
# PAGE CONFIG
# -------------------------------
def setup_page(title="SQL Optimizer"):
    st.set_page_config(page_title=title, layout="wide")


# -------------------------------
# GROQ CLIENT
# -------------------------------
# client = Groq(api_key="API_KEY_HERE")  # replace with your actual API key
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
