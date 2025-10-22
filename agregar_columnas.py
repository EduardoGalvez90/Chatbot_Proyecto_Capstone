import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('restaurantes.db')
cursor = conn.cursor()

# Agregar las columnas faltantes a la tabla 'restaurantes'
cursor.execute("""
    ALTER TABLE restaurantes
    ADD COLUMN horario_apertura TEXT;
""")
cursor.execute("""
    ALTER TABLE restaurantes
    ADD COLUMN menu TEXT;
""")
cursor.execute("""
    ALTER TABLE restaurantes
    ADD COLUMN platos_especiales TEXT;
""")

# Confirmar cambios
conn.commit()

# Cerrar la conexión
conn.close()

print("✅ Columnas agregadas exitosamente.")
