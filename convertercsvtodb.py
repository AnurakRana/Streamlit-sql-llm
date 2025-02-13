import pandas as pd
import sqlite3

# Load CSV into DataFrame
csv_file = "data.csv"  # Change this to your CSV file path
df = pd.read_csv("employee.csv")

# Connect to SQLite database (or create it)
db_file = "employeedata.db"
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Create a table (Modify column names and types as needed)
df.to_sql("Employee", conn, if_exists="replace", index=False)

# Commit and close the connection
conn.commit()
conn.close()

print("CSV successfully converted to SQLite database!")
