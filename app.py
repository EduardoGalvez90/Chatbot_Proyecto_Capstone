from flask import Flask, render_template, request, jsonify
import sqlite3
import google.generativeai as genai
import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("models/gemini-2.0-flash")

ultimo_plato = None

SINONIMOS = {
    "chancho": "cerdo",
    "chicharron": "chicharrón",
    "cuy horneado": "cuy al horno",
    "trucha": "trucha frita",
    "caldo verde": "sopa verde",
    "sopa verde": "caldo verde",
    "cabrito": "seco de cabrito",
    "cerdo": "chicharrón de cerdo",
    "cuy": "cuy frito",
    "gallina": "caldo de gallina",
    "chochoca": "sopa de trigo"
}

VOCAB_COMIDA = [
    "cuy", "cuy frito", "cuy al horno", "chicharrón", "chicharron", "trucha", "trucha frita",
    "caldo", "caldo de gallina", "caldo verde", "sopa", "sopa de morón", "sopa de quinua",
    "sopa de trigo", "quinua", "trigo", "cabrito", "seco de cabrito", "ceviche", "pollo a la brasa",
    "cerdo", "chancho", "cabeza", "caldo de cabeza"
]

STOPWORDS = {
    "donde", "dónde", "puedo", "quiero", "comer", "probar", "un", "una", "el", "la", "los", "las",
    "de", "del", "al", "en", "para", "por", "porfavor", "por favor", "me", "da", "dame", "hay", "tengo",
    "que", "y", "o", "con", "sin", "a", "quiero comer", "quiero probar"
}

def normalizar_plato(texto):
    texto = texto.lower().strip()
    texto = re.sub(r"[^\w\sáéíóúñ]", "", texto)
    for clave, valor in SINONIMOS.items():
        if clave in texto:
            return valor
    return texto

def buscar_restaurantes(plato):
    conexion = sqlite3.connect("restaurantes.db")
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT nombre, direccion, tipos_comida, horario_apertura, menu, platos_especiales, lat, lon
        FROM restaurantes 
        WHERE LOWER(tipos_comida) LIKE ? OR LOWER(nombre) LIKE ? OR LOWER(menu) LIKE ?
    """, (f'%{plato.lower()}%', f'%{plato.lower()}%', f'%{plato.lower()}%'))
    resultados = cursor.fetchall()
    print(f"Resultados (simple) para '{plato}': {resultados}")
    conexion.close()
    return resultados

def listar_todos_restaurantes():
    conexion = sqlite3.connect("restaurantes.db")
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT nombre, direccion, tipos_comida, horario_apertura, menu, platos_especiales, lat, lon
        FROM restaurantes
        ORDER BY nombre ASC
    """)
    resultados = cursor.fetchall()
    conexion.close()
    return resultados

def extraer_keywords_plato(texto):
    t = texto.lower()
    t = re.sub(r"[^\w\sáéíóúñ]", " ", t)
    partes = [p for p in t.split() if p and p not in STOPWORDS]
    keywords = partes[:]
    for i in range(len(partes)-1):
        bigrama = partes[i] + " " + partes[i+1]
        keywords.append(bigrama)
    seen = set()
    limpios = []
    for k in keywords:
        if k not in seen:
            seen.add(k)
            limpios.append(k)
    return limpios

def buscar_restaurantes_por_keywords(keywords):
    if not keywords:
        return []
    filtradas = [k for k in keywords if len(k) >= 3]
    if not filtradas:
        return []
    conexion = sqlite3.connect("restaurantes.db")
    cursor = conexion.cursor()
    condiciones = []
    params = []
    for k in filtradas:
        condiciones.append("(LOWER(menu) LIKE ? OR LOWER(tipos_comida) LIKE ?)")
        like = f"%{k.lower()}%"
        params.extend([like, like])
    where = " OR ".join(condiciones)
    sql = f"""
        SELECT nombre, direccion, tipos_comida, horario_apertura, menu, platos_especiales, lat, lon
        FROM restaurantes
        WHERE {where}
    """
    print("SQL dinámico:", sql)
    print("Params:", params)
    cursor.execute(sql, params)
    resultados = cursor.fetchall()
    conexion.close()
    return resultados

def es_saludo(texto):
    t = texto.lower()
    return any(p in t for p in ["hola", "buenas", "hey", "qué tal", "buenos días", "buenas tardes"])

def es_agradecimiento(texto):
    t = texto.lower()
    return any(p in t for p in ["gracias", "muchas gracias", "te agradezco"])

def es_recomendacion_general(texto):
    t = texto.lower()
    return any(p in t for p in ["recomiend", "suger", "aconsej", "lugares para comer", "quiero comer"])

def es_donde_comer(texto):
    t = texto.lower()
    return ("donde" in t or "dónde" in t) or ("comer" in t) or ("probar" in t)

def contiene_vocab_comida(texto):
    t = texto.lower()
    return any(v in t for v in VOCAB_COMIDA)

def es_pedir_listado_lugares(texto: str) -> bool:
    t = texto.lower()
    patrones = [
        "lugares donde comer",
        "lugares para comer",
        "donde almorzar",
        "dónde almorzar",
        "sitios para comer",
        "restaurantes cerca",
        "restaurantes disponibles",
        "lista de restaurantes",
        "todos los restaurantes",
        "recomiendame restaurantes",
        "recomiéndame restaurantes"
    ]
    return any(p in t for p in patrones)

def traducir_texto(texto, idioma_destino="en"):
    url = "https://libretranslate.de/translate"
    params = {
        "q": texto,
        "source": "es",  # Español por defecto
        "target": idioma_destino  # Idioma de destino
    }

    try:
        response = requests.post(url, params=params)
        print(f"Request sent to LibreTranslate with response code: {response.status_code}")

        # Verificar que la respuesta de la API no esté vacía o mal formada
        if response.status_code == 200:
            data = response.json()
            if 'translatedText' in data:
                return data['translatedText']
            else:
                print("No se encontró el campo 'translatedText' en la respuesta.")
                return "Error en la traducción"
        else:
            print(f"Error en la API de traducción, código de respuesta: {response.status_code}")
            return "Error al traducir, la API no respondió correctamente"

    except Exception as e:
        print(f"Error al conectar con la API de traducción: {e}")
        return "Error en la conexión con la API de traducción"

@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/send_message", methods=["POST"])
def send_message():
    global ultimo_plato

    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"response": "No se recibió mensaje válido."}), 400

    user_message = data["message"].lower().strip()
    respuesta = ""

    if "ferreteria" in user_message or "salud" in user_message or "noticias" in user_message:
        return jsonify({"response": "❌ Lo siento, solo puedo responder preguntas sobre gastronomía de Cajamarca, platos típicos y restaurantes en la región."})

    if es_saludo(user_message):
        return jsonify({"response": "👋 ¡Hola! Soy tu asistente gastronómico de Cajamarca. ¿Qué plato típico te gustaría probar hoy?"})

    if es_agradecimiento(user_message):
        return jsonify({"response": "😊 ¡De nada! Me alegra poder ayudarte. ¿Quieres que te recomiende otro plato o restaurante?"})

    # Respuestas relacionadas con lugares para comer
    if es_donde_comer(user_message) or "quiero" in user_message or contiene_vocab_comida(user_message):
        candidato = normalizar_plato(user_message)
        resultados = buscar_restaurantes(candidato)
        if not resultados:
            keywords = extraer_keywords_plato(user_message)
            resultados = buscar_restaurantes_por_keywords(keywords)
        if resultados:
            ultimo_plato = candidato
            nombre_plato_mostrar = None
            for v in VOCAB_COMIDA:
                if v in user_message:
                    nombre_plato_mostrar = v
                    break
            titulo = nombre_plato_mostrar if nombre_plato_mostrar else candidato
            partes = [f"🍽️ Aquí tienes opciones para disfrutar de {titulo}:"]

            for (nombre, direccion, tipo, horario, menu, especiales, lat, lon) in resultados:
                horario = horario or "Horario no disponible"
                menu = menu or "Menú no disponible"
                especiales = especiales or "Platos especiales no disponibles"
                partes.append(
                    f"🏠 {nombre}\n📍 {direccion}\n🍽️ {tipo}\n⏰ Horarios: {horario}\n🍴 Menú: {menu}\n🌟 Platos Especiales: {especiales}"
                )
            return jsonify({"response": " ".join(partes)})

    if es_pedir_listado_lugares(user_message):
        todos = listar_todos_restaurantes()
        if not todos:
            return jsonify({"response": "😕 No tengo restaurantes registrados aún."})
        partes = ["📍 Estos son los restaurantes registrados:"]
        for (nombre, direccion, tipo, horario, menu, especiales, lat, lon) in todos:
            horario = horario or "Horario no disponible"
            partes.append(f"🏠 {nombre} \n📍 {direccion}\n🍽️ {tipo}\n⏰ {horario}")
        return jsonify({"response": " \n\n".join(partes)})

    if es_recomendacion_general(user_message):
        return jsonify({
            "response": (
                "🍽️ Aquí tienes algunos lugares populares en Cajamarca:\n"
                "🏠 El Cumbe – Jr. Del Comercio 456 (Cuy frito, Caldo verde)\n"
                "🏠 Sabores del Inca – Jr. Puga 987 (Sopa de morón, Cuy frito)\n"
                "🏠 La Collpa – Baños del Inca Km 5 (Trucha frita, Chicharrón de cerdo)\n"
                "🏠 El Porongo – Jr. Cruz de Piedra 416 (Ceviche, Trucha Frita)\n"
                "🏠 Rokys – Av. Hoyos Rubio 950 (Pollo a la brasa)"
            )
        })

    # Si el usuario no hizo una pregunta relacionada con la gastronomía, el modelo responde con una advertencia
    try:
        prompt = f"Eres un asistente gastronómico especializado en la gastronomía de Cajamarca. Responde solo con información sobre platos típicos de Cajamarca, restaurantes, y todo lo relacionado con la comida de la región. No respondas sobre otros temas. El usuario dice: '{user_message}'"

        respuesta_ia = model.generate_content(prompt)
        respuesta = respuesta_ia.text.strip()
    except Exception as e:
        print("Error Gemini:", e)
        respuesta = "No entendí bien tu mensaje. Solo puedo responder preguntas sobre la gastronomía de Cajamarca."

    return jsonify({"response": respuesta})

@app.route("/translate", methods=["POST"])
def translate():
    data = request.get_json()
    if "message" not in data or "language" not in data:
        return jsonify({"response": "Error: Datos incompletos."}), 400

    # Traducción al idioma seleccionado
    message = data["message"]
    idioma_destino = data["language"]  # "en", "pt", "fr"...

    translated_text = traducir_texto(message, idioma_destino)
    if translated_text:
        return jsonify({"response": translated_text})
    return jsonify({"response": "Error al traducir el mensaje."})

if __name__ == "__main__":
    app.run(debug=True)
