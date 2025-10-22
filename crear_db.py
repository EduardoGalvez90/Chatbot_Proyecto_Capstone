import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('restaurantes.db')
cursor = conn.cursor()

# Crear la tabla 'restaurantes' con todas las columnas necesarias
cursor.execute("""
CREATE TABLE IF NOT EXISTS restaurantes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    direccion TEXT NOT NULL,
    tipos_comida TEXT NOT NULL,
    lat REAL,
    lon REAL,
    horario_apertura TEXT,
    menu TEXT,
    platos_especiales TEXT
)
""")

# Confirmar cambios
conn.commit()

# Cerrar la conexión
conn.close()

print("✅ Estructura de la base de datos creada correctamente.")
