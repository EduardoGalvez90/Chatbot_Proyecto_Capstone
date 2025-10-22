import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('restaurantes.db')
cursor = conn.cursor()

# Agregar las columnas faltantes a la tabla 'restaurantes'
cursor.execute("""
    ALTER TABLE restaurantes
    ADD COLUMN lat REAL;
""")
cursor.execute("""
    ALTER TABLE restaurantes
    ADD COLUMN lon REAL;
""")

# Confirmar cambios
conn.commit()

# Cerrar la conexión
conn.close()

print("✅ Columnas 'lat' y 'lon' agregadas exitosamente.")
