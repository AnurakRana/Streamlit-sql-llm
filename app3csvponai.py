import streamlit as st
import pandas as pd
import google.generativeai as generativeai
from pandasql import sqldf
from datetime import datetime
import json
import dialogflow_v2 as dialogflow
from google.oauth2 import service_account


# Configure Gemini API
generativeai.configure(api_key="AIzaSyARzMISJXR6KMQeQ-SEV4Ns0c73MPN_ak4")

# Load Dialogflow credentials
dialogflow_credentials = service_account.Credentials.from_service_account_file("dialogflow_key.json")
dialogflow_session_client = dialogflow.SessionsClient(credentials=dialogflow_credentials)
DIALOGFLOW_PROJECT_ID = "project=currencybot-test-atmi"


# Read CSV file
df = pd.read_csv("sample_data.csv", dtype={"Date": str})

# Define Schema
schema_info = "Table: df\nColumns:\n" + "\n".join([f"- {col} ({df[col].dtype})" for col in df.columns])

# Function to Parse Date
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

# Convert Date column
df['Date'] = df['Date'].apply(parse_date)
df['Date'] = df['Date'].apply(lambda x: x.strftime('%d-%m-%Y') if pd.notna(x) else None)

# Convert CityCode to integer
df['CityCode'] = df['CityCode'].astype(int)

df.info()  # Display DataFrame information

prompt = f"""
remember the format of date is d-m-y
do not add anything extra just the sql command
You are an expert in converting English questions into SQL queries!
The MySQL database contains the following tables and columns:
{schema_info}
For example:
- "How many employees are in the Employee table?" → SELECT COUNT(*) FROM Employee;
- "Show all students from the STUDENT table." → SELECT * FROM STUDENT;
DO NOT AT ALL COST ADD ' IN FRONT OR BACK OF THE CODE
Only return the SQL query, without additional text or explanations.
Remember to use simple commands like SHOW TABLES.
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

    st.subheader("Query Results")
    st.dataframe(result)

    # Convert DataFrame to JSON
    result_json = result.to_json(orient="records")


    def send_to_dialogflow(session_id, text):
        session = dialogflow_session_client.session_path(DIALOGFLOW_PROJECT_ID, session_id)
        text_input = dialogflow.types.TextInput(text=text, language_code="en")
        query_input = dialogflow.types.QueryInput(text=text_input)
        response = dialogflow_session_client.detect_intent(session=session, query_input=query_input)
        return response.query_result.fulfillment_text

    dialogflow_response = send_to_dialogflow("12345", f"SQL Query: {sql_query}\nResults: {result_json}")
    
    st.subheader("Dialogflow Response")
    st.write(dialogflow_response)
