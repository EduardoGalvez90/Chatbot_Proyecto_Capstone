import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('restaurantes.db')
cursor = conn.cursor()

# Insertar datos de ejemplo
cursor.execute("""
INSERT INTO restaurantes (nombre, direccion, tipos_comida, lat, lon, horario_apertura, menu, platos_especiales)
VALUES
    ('La Terraza Andina', 'Av. Mario Urteaga 852, Cajamarca', 'Chicharrón, Caldo verde, Seco de cabrito', -7.1478, -78.5152, 
     'Lunes a Sábado: 12:00 PM - 10:00 PM', 'Chicharrón, Caldo verde, Seco de cabrito', 'Menú del día: Seco de cabrito y arroz'),
    ('El Porongo', 'Jr. Cruz de Piedra 416, Cajamarca', 'Trucha frita, Ceviche, Chicharrón', -7.1430, -78.5175,
     'Martes a Domingo: 10:00 AM - 8:00 PM', 'Trucha frita, Ceviche, Chicharrón', 'Plato especial: Ceviche con chicharrón de cerdo'),
    ('Rokys', 'Av. Hoyos Rubio 950, Cajamarca', 'Pollo a la brasa', -7.1455, -78.5190,
     'Lunes a Domingo: 12:00 PM - 10:00 PM', 'Pollo a la brasa, Papas fritas, Ensalada', 'Promoción de pollo a la brasa con bebida'),
    ('El Tío Juan', 'Jr. Sucre 147, Cajamarca', 'Cuy frito, Caldo de cabeza, Trucha frita', -7.1486, -78.5182,
     'Lunes a Sábado: 11:00 AM - 9:00 PM', 'Cuy frito, Caldo de cabeza, Trucha frita', 'Menú del día: Trucha frita y sopa de quinua'),
    ('Doña Julia', 'Jr. Dos de Mayo 556, Cajamarca', 'Caldo de gallina, Sopa de trigo, Chicharrón de chancho', -7.1452, -78.5160,
     'Miércoles a Lunes: 10:00 AM - 8:00 PM', 'Caldo de gallina, Sopa de trigo, Chicharrón de chancho', 'Plato especial: Caldo de gallina con arroz'),
    ('El Encuentro', 'Plaza de Armas 123, Cajamarca', 'Cuy al horno, Caldo de cabeza, Seco de res', -7.1460, -78.5180,
     'Jueves a Domingo: 1:00 PM - 9:00 PM', 'Cuy al horno, Caldo de cabeza, Seco de res', 'Plato especial: Seco de res con papa dorada')
""")

# Confirmar cambios
conn.commit()

# Cerrar la conexión
conn.close()

print("✅ Datos insertados correctamente en la base de datos.")
