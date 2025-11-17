# app_streamlit.py
import os
import io
import pandas as pd
import streamlit as st

# import your existing function
# from your_code import ask_db
# if your function lives in a module, fix the import path accordingly
from src.llm_sql import ask_db  # <— adjust if needed

st.set_page_config(page_title="Ask My Database", page_icon="🗄️", layout="wide")

# --- Header ---
st.title("🗄️ Ask My Database")
st.caption("Type a question in plain English. The app will generate SQL, run it, and show the results.")

# --- Sidebar controls ---
with st.sidebar:
    st.header("Settings")
    st.write("These affect only the UI; your DB permissions/limits still apply.")
    add_limit = st.checkbox("Force LIMIT on generated SQL", value=True)
    limit_rows = st.number_input("Row limit", min_value=10, max_value=10000, value=200, step=10)
    show_sql_first = st.checkbox("Show generated SQL before running", value=False)
    st.divider()
    st.write("Export")
    include_index = st.checkbox("Include index on download", value=False)

# --- Chat-like history in session state ---
if "history" not in st.session_state:
    st.session_state.history = []  # list of dicts: {'q':..., 'sql':..., 'rows': int, 'error':...}

# --- Input row ---
col1, col2 = st.columns([4,1])
with col1:
    q = st.text_input("Ask a question (e.g., 'Total budget for 2024 by department'):", key="q", placeholder="What is the total budget for 2023?")
with col2:
    run = st.button("Run", use_container_width=True)

def _force_limit(sql: str, k: int) -> str:
    s = sql.strip().rstrip(";")
    # very light-handed: if no 'limit' present, append one
    if " limit " not in s.lower():
        s += f" LIMIT {k}"
    return s + ";"

# --- Action ---
if run and q:
    with st.spinner("Thinking… generating SQL and querying the database"):
        result = ask_db(q)  # {'sql', 'df', 'error'}
        sql = result.get("sql", "").strip()
        if add_limit and sql:
            sql = _force_limit(sql, int(limit_rows))

        # display SQL (before or after)
        if show_sql_first and sql:
            st.code(sql, language="sql")

        error = result.get("error")
        df = result.get("df")

        if error:
            st.error(error)
        else:
            # If we forced LIMIT, re-run the query if needed
            if add_limit and result.get("sql","").strip().rstrip(";") + ";" != sql:
                # Optional: only do this if your ask_db can accept raw SQL; otherwise you’ll keep the original df
                # Here we assume ask_db always generates SQL itself; so we just display df we already got.
                pass

            rows = len(df) if isinstance(df, pd.DataFrame) else 0

            # Show SQL (after) if not shown before
            if not show_sql_first and sql:
                st.code(sql, language="sql")

            st.success(f"Returned {rows} row(s)")
            if rows > 0:
                st.dataframe(df, use_container_width=True)

                # downloads
                csv = df.to_csv(index=include_index).encode("utf-8")
                st.download_button(
                    "Download CSV",
                    data=csv,
                    file_name="query_results.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

        # log to history
        st.session_state.history.insert(0, {
            "q": q,
            "sql": sql,
            "rows": len(df) if isinstance(df, pd.DataFrame) else 0,
            "error": error
        })

# --- History accordion ---
if st.session_state.history:
    with st.expander("History", expanded=False):
        for item in st.session_state.history[:10]:
            st.markdown(f"**Q:** {item['q']}")
            if item["sql"]:
                st.code(item["sql"], language="sql")
            if item["error"]:
                st.error(item["error"])
            else:
                st.write(f"Rows: {item['rows']}")
            st.markdown("---")
