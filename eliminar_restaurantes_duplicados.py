import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('restaurantes.db')
cursor = conn.cursor()

# Eliminar registros duplicados
cursor.execute("DELETE FROM restaurantes WHERE nombre = 'Restaurante El Cumbe '")

# Confirmar cambios
conn.commit()

# Cerrar la conexión
conn.close()

print("✅ Registros duplicados eliminados.")
