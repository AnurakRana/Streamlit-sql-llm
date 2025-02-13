import sqlite3

conn = sqlite3.connect("Northwind.db")

cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS Customers (
                    ID INTEGER PRIMARY KEY,
                    Name TEXT NOT NULL
                )''')

conn.commit()
conn.close()

print("Database created successfully!")
