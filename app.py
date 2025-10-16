from flask import Flask, render_template, request, jsonify
import sqlite3
import google.generativeai as genai
import os
import re
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# 🔹 Configurar API de Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("models/gemini-2.0-flash")

ultimo_plato = None

# -------------------------------
# SINÓNIMOS DE PLATOS
# -------------------------------
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

# -------------------------------
# FUNCIONES DE UTILIDAD
# -------------------------------
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
        SELECT nombre, direccion, tipos_comida 
        FROM restaurantes 
        WHERE LOWER(tipos_comida) LIKE ? OR LOWER(nombre) LIKE ?
    """, ('%' + plato.lower() + '%', '%' + plato.lower() + '%'))
    resultados = cursor.fetchall()
    conexion.close()
    return resultados

# -------------------------------
# DETECCIÓN DE INTENCIÓN
# -------------------------------
def es_saludo(texto):
    return any(p in texto for p in ["hola", "buenas", "hey", "qué tal", "buenos días", "buenas tardes"])

def es_agradecimiento(texto):
    return any(p in texto for p in ["gracias", "muchas gracias", "te agradezco"])

def es_recomendacion_general(texto):
    return any(p in texto for p in ["recomiend", "suger", "aconsej", "lugares para comer", "quiero comer"])

# -------------------------------
# RUTAS
# -------------------------------
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

    # 👋 SALUDO
    if es_saludo(user_message):
        return jsonify({"response": "👋 ¡Hola! Soy tu asistente gastronómico de Cajamarca. ¿Qué plato típico te gustaría probar hoy?"})

    # 🙏 AGRADECIMIENTO
    if es_agradecimiento(user_message):
        return jsonify({"response": "😊 ¡De nada! Me alegra poder ayudarte. ¿Quieres que te recomiende otro plato o restaurante?"})

    # 🍽️ RECOMENDACIONES GENERALES
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

    # 🔍 BÚSQUEDA DE PLATOS
    if any(p in user_message for p in ["dónde", "donde", "quiero", "comer", "probar"]):
        plato = normalizar_plato(user_message)
        resultados = buscar_restaurantes(plato)
        if resultados:
            ultimo_plato = plato
            respuesta = f"🍽️ Aquí tienes opciones para disfrutar de {plato}:\n"
            for nombre, direccion, tipo in resultados:
                respuesta += f"🏠 {nombre}\n📍 {direccion}\n🍽️ {tipo}\n\n"
            return jsonify({"response": respuesta})
        else:
            return jsonify({"response": f"😕 No encontré lugares con {plato}, pero puedo recomendarte cuy frito o caldo verde."})

    # 🧠 RESPUESTA DE GEMINI
    try:
        respuesta_ia = model.generate_content(f"Eres un asistente gastronómico en Cajamarca. El usuario dice: '{user_message}'.")
        respuesta = respuesta_ia.text.strip()
    except Exception as e:
        print("Error Gemini:", e)
        respuesta = "No entendí bien tu mensaje. Puedo ayudarte con información sobre los mejores platos y restaurantes en Cajamarca."

    return jsonify({"response": respuesta})

if __name__ == "__main__":
    app.run(debug=True)
