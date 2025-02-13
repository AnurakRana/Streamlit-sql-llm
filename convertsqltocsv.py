import pandas as pd
import mysql.connector

# Connect to the database
db = mysql.connector.connect(user='root',password='Arana@1993', database='northwind')
cursor = db.cursor()

# Fetch all columns dynamically
query = "SELECT * FROM employee"
cursor.execute(query)

# Get column names
columns = [desc[0] for desc in cursor.description]

# Fetch all data
all_data = cursor.fetchall()

# Convert data into a DataFrame
df = pd.DataFrame(all_data, columns=columns)

# Save DataFrame to CSV
csv_file_path = 'D:/LLMSQL/employee.csv'
df.to_csv(csv_file_path, index=False, encoding='utf-8')

print(f"Data successfully saved to {csv_file_path}")
