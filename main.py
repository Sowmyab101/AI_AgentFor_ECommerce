import os
import sqlite3
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

# Loading environment variables from .env
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# Gemini prompt template
PROMPT_TEMPLATE = """
You are an assistant that converts user questions into pure SQLite queries.

Use only these tables and columns:

- ad_sales(date, item_id, ad_sales, impressions, ad_spend, clicks, units_sold)
- total_sales(date, item_id, total_sales, total_units_ordered)
- eligibility(eligibility_datetime_utc, item_id, eligibility, message)

Only return a valid SQLite SQL query. Do not explain, format, or comment.
Question: {question}
"""

# Function: To Get SQL from Gemini
def question_to_sql(question):
    prompt = PROMPT_TEMPLATE.format(question=question)
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"ERROR: {str(e)}"

# Function: To Run SQL on SQLite
def run_sql(sql_query):
    try:
        conn = sqlite3.connect("ecommerce1.db")
        df = pd.read_sql_query(sql_query, conn)
        conn.close()
        return df
    except Exception as e:
        return f"SQL ERROR: {str(e)}"

# Streamlit 
st.set_page_config("E-commerce AI Agent", layout="centered")
st.title("🛒 E-commerce AI Agent (Gemini + SQLite)")

question = st.text_input("💬 Ask a question about your data:")

if st.button("Ask Gemini") and question:
    with st.spinner("🤖 Thinking..."):
        # Step 1: Gemini generates SQL
        sql = question_to_sql(question)

        if sql.startswith("ERROR"):
            st.error(sql)
        else:
            # Step 2: Run SQL
            result = run_sql(sql)

            if isinstance(result, pd.DataFrame) and not result.empty:
                # Step 3: Converting table to string
                table_text = result.to_string(index=False)

                # Step 4: Asking Gemini to explain result in plain English
                explain_prompt = f"Explain this SQL result in a clear, human-readable sentence:\n\n{table_text}"

                try:
                    explanation = model.generate_content(explain_prompt).text.strip()
                except Exception as e:
                    explanation = f"ERROR: {e}"

                st.subheader("🧠 Final Answer")
                st.success(explanation)
            else:
                st.warning("⚠️ No results found or query failed.")
