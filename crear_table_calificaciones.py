import sqlite3

conn = sqlite3.connect("restaurantes.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS calificaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    puntuacion INTEGER NOT NULL CHECK (puntuacion >= 1 AND puntuacion <= 5),
    comentario TEXT,
    fecha TEXT NOT NULL
)
""")

conn.commit()
conn.close()
print("✅ Tabla 'calificaciones' creada (o ya existía).")
