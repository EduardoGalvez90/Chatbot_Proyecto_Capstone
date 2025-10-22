import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('restaurantes.db')
cursor = conn.cursor()

# Eliminar todos los registros de la tabla 'restaurantes'
cursor.execute("DELETE FROM restaurantes")

# Confirmar cambios
conn.commit()

# Cerrar la conexión
conn.close()

print("✅ Todos los registros de la base de datos han sido eliminados.")
