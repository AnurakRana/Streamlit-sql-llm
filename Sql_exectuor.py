import sqlite3

conn = sqlite3.connect("Northwind.db")
cursor = conn.cursor()

with open("northwind.sql", "r") as file:
    sql_script = file.read()

cursor.executescript(sql_script)
conn.commit()
conn.close()

print("SQL file executed successfully!")
