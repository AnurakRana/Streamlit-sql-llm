import streamlit as st
import pandas as pd
import google.generativeai as generativeai
from pandasql import sqldf
from datetime import datetime

# ✅ Configure Gemini AI API Key
generativeai.configure(api_key="AIzaSyARzMISJXR6KMQeQ-SEV4Ns0c73MPN_ak4")  

# ✅ Read CSV
df = pd.read_csv("sample_data.csv", dtype={"Date": str})  

# ✅ Schema Information
schema_info = "Table: df\nColumns:\n" + "\n".join([f"- {col} ({df[col].dtype})" for col in df.columns])

# ✅ Convert Date Column
def parse_date(date_str):
    if isinstance(date_str, pd.Timestamp):  
        return date_str
    if pd.isna(date_str):  
        return None  
    for fmt in ('%m/%d/%Y', '%d-%m-%Y'):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None  

df['Date'] = df['Date'].apply(parse_date)
df['Date'] = df['Date'].apply(lambda x: x.strftime('%d-%m-%Y') if pd.notna(x) else None)

# ✅ Ensure CityCode is an Integer
df['CityCode'] = df['CityCode'].astype(int)

# ✅ Display Updated Data Types
df.info()

# ✅ Gemini AI Prompt
prompt = f"""
You are an expert in converting English questions into SQL queries!
The MySQL database contains the following tables and columns:
{schema_info}
Only return the SQL query, without additional text or explanations.
The date format should be 'DD-MM-YYYY'.
Do not run DROP or DELETE commands.
"""

# ✅ Streamlit UI
st.set_page_config(page_title="CSV SQL Query Generator")
st.header("Gemini SQL Query Generator (CSV)")

question = st.text_input("Hey there! Ask a question about your data:")
submit = st.button("Generate Query")

if submit and question:
    # ✅ Generate SQL Query using Gemini
    model = generativeai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt, question])
    
    # ✅ Extract SQL Query
    sql_query = response.text.strip().split(";")[0] 
    st.subheader("Generated SQL Query")
    st.code(sql_query, language="sql")
    
    # ✅ Run SQL Query on DataFrame
    result = sqldf(sql_query, {"df": df}) 

    # ✅ Find Row Indices in Original DataFrame
    matching_indices = df[df.apply(lambda row: row.tolist() in result.values.tolist(), axis=1)].index.tolist()
    
    st.subheader("Query Results")
    st.dataframe(result)

    st.subheader("Matching Row Indices from Original CSV")
    st.write(matching_indices)
