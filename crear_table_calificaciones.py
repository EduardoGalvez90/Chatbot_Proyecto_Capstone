import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('restaurantes.db')
cursor = conn.cursor()

# Inserción de datos de ejemplo
cursor.execute("""
INSERT INTO restaurantes (nombre, direccion, tipos_comida, lat, lon, horario_apertura, menu, platos_especiales)
VALUES
    ('Restaurante El Cumbe', 'Jr. Del Comercio 456, Cajamarca', 'Cuy frito, Caldo verde, Chicharrón', -7.1445, -78.5210, 
     'Lunes a Domingo: 11:00 AM - 10:00 PM', 'Cuy frito, Caldo verde, Chicharrón', 'Menú especial del día: Sopa de morón y Cuy frito')
""")

conn.commit()
conn.close()

print("✅ Datos de ejemplo insertados correctamente.")
