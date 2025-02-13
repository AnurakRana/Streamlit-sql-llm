import streamlit as st
import pandas as pd
import google.generativeai as generativeai
from pandasql import sqldf
from datetime import datetime

generativeai.configure(api_key="")  

df = pd.read_csv("sample_data.csv", dtype={"Date": str})  

schema_info = "Table: df\nColumns:\n" + "\n".join([f"- {col} ({df[col].dtype})" for col in df.columns])

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

df['CityCode'] = df['CityCode'].astype(int)

df.info()

prompt = f"""
You are an expert in converting English questions into SQL queries!
The MySQL database contains the following tables and columns:
{schema_info}
Only return the SQL query, without additional text or explanations.
The date format should be 'DD-MM-YYYY'.
Do not run DROP or DELETE commands.
"""

st.set_page_config(page_title="CSV SQL Query Generator")
st.header("Gemini SQL Query Generator (CSV)")

question = st.text_input("Hey there! Ask a question about your data:")
submit = st.button("Generate Query")

if submit and question:
    model = generativeai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt, question])
    
    sql_query = response.text.strip().split(";")[0] 
    st.subheader("Generated SQL Query")
    st.code(sql_query, language="sql")
    
    result = sqldf(sql_query, {"df": df}) 

    matching_indices = df[df.apply(lambda row: row.tolist() in result.values.tolist(), axis=1)].index.tolist()
    
    st.subheader("Query Results")
    st.dataframe(result)

    st.subheader("Matching Row Indices from Original CSV")
    st.write(matching_indices)
