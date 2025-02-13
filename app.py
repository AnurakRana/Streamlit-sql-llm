import streamlit as st
import pymysql
import os
from dotenv import load_dotenv
import google.generativeai as generativeai

generativeai.configure(api_key="")

DB_HOST = ""
DB_USER = ""
DB_PASSWORD = ""
DB_NAME = ""

# ALLOWED_SQL_PATTERNS = [
#     r"^\s*SELECT\s+\*?\s+FROM\s+\w+",   # SELECT * FROM table
#     r"^\s*SHOW\s+TABLES\s*$",           # SHOW TABLES
#     r"^\s*SHOW\s+COLUMNS\s+FROM\s+\w+"  # SHOW COLUMNS FROM table
# ]

# FORBIDDEN_KEYWORDS = ["DROP", "DELETE", "INSERT", "UPDATE", "--", "#", ";", "/*", "*/"]


# def is_valid_sql(sql_query):
#     """
#     Validates AI-generated SQL queries.
#     Ensures:
#       - Only SELECT or SHOW queries are allowed
#       - No semicolons, comments, or unsafe keywords
#     """
#     sql_query = sql_query.strip().upper()

#     # Check for forbidden keywords
#     for keyword in FORBIDDEN_KEYWORDS:
#         if keyword in sql_query:
#             return False

#     # Check allowed patterns
#     return any(re.match(pattern, sql_query, re.IGNORECASE) for pattern in ALLOWED_SQL_PATTERNS)


def get_gemini_response(question, prompt):
    model = generativeai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt, question])
    sql_query=response.text.strip()
    sql_query=sql_query.split(";")[0]
    # if not is_valid_sql(sql_query):
    #     return "ERROR: AI generated an invalid or unsafe query!"
    return sql_query

def read_sql_query(sql):
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )
    cur = conn.cursor()
    
    try:
        cur.execute(sql)
        rows = cur.fetchall()
    except pymysql.MySQLError as e:
        rows = [{"Error": str(e)}]
    
    conn.close()
    return rows

def get_table_info():
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cur = conn.cursor()
    
    cur.execute("SHOW TABLES;")
    tables = cur.fetchall()
    
    schema = {}
    for (table_name,) in tables:
        cur.execute(f"DESCRIBE {table_name};")
        columns = cur.fetchall()
        schema[table_name] = [col[0] for col in columns]  
    
    conn.close()
    return schema

table_schema = get_table_info()

schema_description = "\n".join(
    [f"Table: {table}, Columns: {', '.join(cols)}" for table, cols in table_schema.items()]
)

prompt = f"""
do not add anything extra just the sql command
You are an expert in converting English questions into SQL queries!
The MySQL database contains the following tables and columns:
{schema_description}
For example:
- "How many employees are in the Employee table?" → SELECT COUNT(*) FROM Employee;
- "Show all students from the STUDENT table." → SELECT * FROM STUDENT;
DO NOT AT ALL COST ADD ' IN FRONT OR BACK OF THE CODE
Only return the SQL query, without additional text or explanations.
remember to use show table or simple commands in the process
and dont run drop or delete commands
"""

st.set_page_config(page_title="SQL Query Generator")
st.header("Gemini SQL Query Generator (MySQL)")

question = st.text_input("Ask a database question:", key="input")
submit = st.button("Generate Query")

if submit:
    sql_query = get_gemini_response(question, prompt)
    
    st.subheader("Generated SQL Query")
    st.code(sql_query, language="sql")

    st.subheader("Query Results")
    data = read_sql_query(sql_query)

    if isinstance(data, list) and len(data) > 0:
        if isinstance(data[0], dict):
            st.dataframe(data)
