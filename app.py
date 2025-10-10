from flask import Flask, render_template, request, jsonify
import sqlite3
import google.generativeai as genai
import os
import re
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
    cursor.execute(
        "SELECT nombre, direccion, tipos_comida FROM restaurantes WHERE LOWER(tipos_comida) LIKE ?",
        ('%' + plato.lower() + '%',)
    )
    resultados = cursor.fetchall()
    conexion.close()
    return resultados

def es_saludo(texto):
    return any(p in texto for p in ["hola", "buenas", "hey", "qué tal", "buenos días", "buenas tardes"])

def es_agradecimiento(texto):
    return any(p in texto for p in ["gracias", "muchas gracias", "te agradezco"])

def es_confirmacion(texto):
    return texto.strip() in ["sí", "si", "claro", "ok", "de acuerdo"]

def es_negacion(texto):
    return texto.strip() in ["no", "nop", "no gracias"]

def es_recomendacion_general(texto):
    return any(p in texto for p in ["recomiend", "suger", "aconsej", "dame un lugar", "un sitio", "lugares para comer", "donde puedo comer"])

@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/send_message", methods=["POST"])
def send_message():
    global ultimo_plato

    user_message = request.json["message"].lower().strip()
    respuesta = ""

    if es_saludo(user_message):
        return jsonify({
            "response": "👋 ¡Hola! Soy tu asistente gastronómico de Cajamarca. ¿Qué plato típico te gustaría probar hoy?"
        })

    if es_agradecimiento(user_message):
        return jsonify({
            "response": "😊 ¡De nada! Me alegra poder ayudarte. ¿Te gustaría que te recomiende otro plato o restaurante de Cajamarca?"
        })

    if es_confirmacion(user_message):
        if ultimo_plato:
            restaurantes = buscar_restaurantes(ultimo_plato)
            if restaurantes:
                respuesta = f"🍽️ Aquí tienes opciones en Cajamarca para disfrutar de **{ultimo_plato}**:\n"
                for nombre, direccion, tipo in restaurantes:
                    respuesta += f"🏠 {nombre}\n📍 {direccion}\n🍽️ Especialidades: {tipo}\n\n"
                respuesta += "¿Deseas que te recomiende otro plato típico o lugar similar?"
                return jsonify({"response": respuesta})
        return jsonify({
            "response": "😊 ¡Perfecto! Dime qué plato te gustaría que te recomiende."
        })

    if es_negacion(user_message):
        ultimo_plato = None
        return jsonify({
            "response": "Está bien 😊. En Cajamarca también puedes probar platos como el **cuy frito**, el **caldo verde** o el **chicharrón**. "
                        "¿Te gustaría información sobre alguno de ellos?"
        })

    if es_recomendacion_general(user_message):
        respuesta = (
            "🍽️ Aquí tienes algunos lugares populares para disfrutar en Cajamarca:\n"
            "🏠 Restaurante El Cumbe – Jr. Del Comercio 456 (Cuy frito, Caldo verde)\n"
            "🏠 Sabores del Inca – Jr. Puga 987 (Cuy frito, Sopa de morón)\n"
            "🏠 La Collpa – Carretera Baños del Inca Km 5 (Trucha frita, Chicharrón de cerdo)\n"
            "🏠 El Porongo – Jr. Cruz de Piedra 416 (Ceviche, Trucha Frita)\n"
            "🏠 Rokys – Av. Hoyos Rubio 950 (Pollo a la brasa)\n\n"
            "¿Quieres que te recomiende según un plato específico?"
        )
        return jsonify({"response": respuesta})

    if any(p in user_message for p in ["dónde", "donde", "quiero", "comer", "probar", "restaurante", "lugar"]):
        plato_encontrado = re.sub(r"(donde|dónde|quiero|comer|probar|restaurante|lugar|puedo|un|una|el|la|\?)", "", user_message).strip()
        plato_normalizado = normalizar_plato(plato_encontrado)

        if not plato_normalizado or plato_normalizado == "":
            respuesta = (
                "🍽️ Aquí tienes algunos lugares populares para disfrutar en Cajamarca:\n"
                "🏠 Restaurante El Cumbe – Jr. Del Comercio 456 (Cuy frito, Caldo verde)\n"
                "🏠 Sabores del Inca – Jr. Puga 987 (Cuy frito, Sopa de morón)\n"
                "🏠 La Collpa – Carretera Baños del Inca Km 5 (Trucha frita, Chicharrón de cerdo)\n"
                "🏠 El Porongo – Jr. Cruz de Piedra 416 (Ceviche, Trucha Frita)\n"
                "🏠 Rokys – Av. Hoyos Rubio 950 (Pollo a la brasa)\n\n"
                "¿Quieres que te recomiende un plato típico de alguno?"
            )
            return jsonify({"response": respuesta})

        resultados = buscar_restaurantes(plato_normalizado)
        if resultados:
            ultimo_plato = plato_normalizado
            respuesta = f"🍽️ Aquí tienes opciones en Cajamarca para disfrutar de **{plato_normalizado}**:\n"
            for nombre, direccion, tipo in resultados:
                respuesta += f"🏠 {nombre}\n📍 {direccion}\n🍽️ Especialidades: {tipo}\n\n"
            respuesta += "¿Deseas que te recomiende otro plato típico o lugar similar?"
        else:
            # Sugerencia si no se encuentra
            ultimo_plato = None
            respuesta = f"😕 No tengo registros exactos de **{plato_encontrado}**, pero puedo recomendar **cuy frito**, **caldo verde** o **chicharrón**. ¿Quieres que te diga dónde probar alguno?"
        return jsonify({"response": respuesta})

    try:
        respuesta_ia = model.generate_content(
            f"Eres un asistente gastronómico en Cajamarca. Responde solo sobre comida local. El usuario dice: '{user_message}'"
        )
        respuesta = respuesta_ia.text.strip()
    except Exception:
        respuesta = "No entendí bien tu mensaje. Puedo ayudarte con información sobre los mejores platos y restaurantes en Cajamarca."

    return jsonify({"response": respuesta})


if __name__ == "__main__":
    app.run(debug=True)
