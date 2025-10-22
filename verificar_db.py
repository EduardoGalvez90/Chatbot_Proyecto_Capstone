import sqlite3

conn = sqlite3.connect('restaurantes.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM restaurantes")
print(cursor.fetchall())

conn.close()
