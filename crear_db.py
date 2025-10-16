# crear_db.py
import sqlite3
from datetime import datetime

conn = sqlite3.connect("restaurantes.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS restaurantes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    direccion TEXT NOT NULL,
    tipos_comida TEXT NOT NULL,
    lat REAL,
    lon REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS calificaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurante_id INTEGER,
    puntuacion INTEGER NOT NULL CHECK (puntuacion >= 1 AND puntuacion <= 5),
    comentario TEXT,
    fecha TEXT NOT NULL,
    FOREIGN KEY (restaurante_id) REFERENCES restaurantes(id)
)
""")

# Si la tabla está vacía, insertar datos de ejemplo (con coordenadas aproximadas en Cajamarca)
cursor.execute("SELECT COUNT(*) FROM restaurantes")
if cursor.fetchone()[0] == 0:
    restaurantes = [
        ("Restaurante El Cumbe", "Jr. Del Comercio 456, Cajamarca", "Cuy frito, Caldo verde, Chicharrón", -7.1445, -78.5210),
        ("Sabores del Inca", "Jr. Puga 987, Cajamarca", "Cuy frito, Sopa de morón, Chicharrón", -7.1470, -78.5200),
        ("La Collpa", "Carretera Baños del Inca Km 5, Cajamarca", "Trucha frita, Caldo de gallina, Chicharrón de cerdo", -7.1030, -78.5340),
        ("El Porongo", "Jr. Cruz de Piedra 416, Cajamarca", "Trucha frita, Ceviche, Chicharrón", -7.1430, -78.5175),
        ("Pikanto", "Jr. Apurímac 678, Cajamarca", "Cuy al horno, Caldo de gallina, Caldo verde", -7.1465, -78.5195),
        ("Los Girasoles", "Av. Atahualpa 123, Cajamarca", "Caldo de cabeza, Sopa verde, Seco de cabrito", -7.1505, -78.5198),
        ("El Capulí", "Av. Hoyos Rubio 321, Cajamarca", "Caldo de gallina, Sopa de quinua, Trucha frita", -7.1408, -78.5242),
        ("La Terraza Andina", "Av. Mario Urteaga 852, Cajamarca", "Chicharrón, Caldo verde, Seco de cabrito", -7.1478, -78.5152),
        ("El Tío Juan", "Jr. Sucre 147, Cajamarca", "Cuy frito, Caldo de cabeza, Trucha frita", -7.1486, -78.5182),
        ("Doña Julia", "Jr. Dos de Mayo 556, Cajamarca", "Caldo de gallina, Sopa de trigo, Chicharrón de chancho", -7.1452, -78.5160),
        ("El Encuentro", "Plaza de Armas 123, Cajamarca", "Cuy al horno, Caldo de cabeza, Seco de res", -7.1460, -78.5180)
    ]
    cursor.executemany(
        "INSERT INTO restaurantes (nombre, direccion, tipos_comida, lat, lon) VALUES (?, ?, ?, ?, ?)",
        restaurantes
    )

# Insertar una calificación de ejemplo (opcional)
cursor.execute("SELECT COUNT(*) FROM calificaciones")
if cursor.fetchone()[0] == 0:
    cursor.execute(
        "INSERT INTO calificaciones (restaurante_id, puntuacion, comentario, fecha) VALUES (?, ?, ?, ?)",
        (1, 5, "Excelente cuy, muy tradicional.", datetime.utcnow().isoformat())
    )

conn.commit()
conn.close()
print("✅ Base de datos 'restaurantes.db' creada y poblada con coordenadas.")
