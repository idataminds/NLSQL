import streamlit as st
import pandas as pd
from graph import graph
from db import get_schema_info

st.set_page_config(page_title="NL to SQL Assistant", page_icon="🤖", layout="wide")

st.title("🤖 Natural Language to SQL")
st.write("Ask in plain English — get SQL and results from your MySQL database.")

# --- Sidebar: Schema Viewer ---
with st.sidebar:
    st.header("📘 Database Schema")
    schema = get_schema_info()
    for table, cols in schema.items():
        st.markdown(f"**{table}**")
        st.markdown(", ".join(cols))
        st.markdown("---")

# --- Main Input ---
question = st.text_input("Enter your question:")

if st.button("Run Query"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Generating SQL and fetching results..."):
            result = graph.invoke({"question": question})

            # SQL query
            st.subheader("🔎 SQL Query")
            st.code(result["sql"], language="sql")

            # Results
            st.subheader("📊 Query Results")
            if isinstance(result["results"], str):
                st.error(result["results"])
            else:
                df = pd.DataFrame(result["results"], columns=result["columns"])
                st.dataframe(df, use_container_width=True)
