import sqlite3

conn = sqlite3.connect("restaurantes.db")
cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS restaurantes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    direccion TEXT NOT NULL,
    tipos_comida TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS calificaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    puntuacion INTEGER NOT NULL CHECK (puntuacion >= 1 AND puntuacion <= 5),
    comentario TEXT,
    fecha TEXT NOT NULL
)
""")

cursor.execute("SELECT COUNT(*) FROM restaurantes")
if cursor.fetchone()[0] == 0:
    restaurantes = [
        ("Restaurante El Cumbe", "Jr. Del Comercio 456, Cajamarca", "Cuy frito, Caldo verde, Chicharrón"),
        ("La Collpa", "Carretera Baños del Inca Km 5, Cajamarca", "Trucha frita, Caldo de gallina, Chicharrón de cerdo"),
        ("Los Girasoles", "Av. Atahualpa 123, Cajamarca", "Caldo de cabeza, Sopa verde, Seco de cabrito"),
        ("Pikanto", "Jr. Apurímac 678, Cajamarca", "Cuy al horno, Caldo de gallina, Caldo verde"),
        ("El Capulí", "Av. Hoyos Rubio 321, Cajamarca", "Caldo de gallina, Sopa de quinua, Trucha frita"),
        ("Sabores del Inca", "Jr. Puga 987, Cajamarca", "Cuy frito, Sopa de morón, Chicharrón"),
        ("La Terraza Andina", "Av. Mario Urteaga 852, Cajamarca", "Chicharrón, Caldo verde, Seco de cabrito"),
        ("El Tío Juan", "Jr. Sucre 147, Cajamarca", "Cuy frito, Caldo de cabeza, Trucha frita"),
        ("Doña Julia", "Jr. Dos de Mayo 556, Cajamarca", "Caldo de gallina, Sopa de trigo, Chicharrón de chancho"),
        ("El Encuentro", "Plaza de Armas 123, Cajamarca", "Cuy al horno, Caldo de cabeza, Seco de res")
    ]
    cursor.executemany(
        "INSERT INTO restaurantes (nombre, direccion, tipos_comida) VALUES (?, ?, ?)",
        restaurantes
    )

conn.commit()
conn.close()

print("✅ Base de datos 'restaurantes.db' creada y poblada con éxito.")
