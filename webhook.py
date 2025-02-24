import os
import sqlite3
import openai
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests

# Configuración
app = Flask(__name__)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
DB_PATH = "reservas.db"

# Inicializar base de datos
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS reservas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT,
                        telefono TEXT,
                        fecha TEXT,
                        hora TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Función para procesar reservas
def procesar_reserva(mensaje, telefono):
    palabras = mensaje.lower().split()
    if "reservar" in palabras:
        try:
            detalles = mensaje.replace("reservar", "").strip()
            partes = detalles.split()
            fecha, hora = partes[0], partes[1]
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO reservas (nombre, telefono, fecha, hora) VALUES (?, ?, ?, ?)",
                           ("Cliente", telefono, fecha, hora))
            conn.commit()
            conn.close()
            return f"Reserva confirmada para el {fecha} a las {hora}. Recibirás un recordatorio antes de tu cita."
        except:
            return "Formato incorrecto. Usa: 'Reservar [fecha] [hora]'"
    return None

# Función para interactuar con OpenRouter
def obtener_respuesta_openrouter(mensaje):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mistralai/mistral-7b-instruct:free",
        "messages": [{"role": "system", "content": "Eres un asistente virtual para una clínica podológica. Tu tarea es ayudar a los pacientes a reservar citas, proporcionar información sobre horarios y disponibilidad, y enviar recordatorios de citas. Sé educado, profesional y útil."},
                      {"role": "user", "content": mensaje}]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"] if response.status_code == 200 else "Error en la respuesta de IA."

# Ruta del webhook para Twilio
@app.route("/webhook", methods=["POST"])
def webhook():
    msg = request.form.get("Body")
    telefono = request.form.get("From")
    
    # Intentar procesar como reserva
    respuesta_reserva = procesar_reserva(msg, telefono)
    if respuesta_reserva:
        return str(MessagingResponse().message(respuesta_reserva))
    
    # Si no es una reserva, responder con IA
    respuesta_ia = obtener_respuesta_openrouter(msg)
    twilio_resp = MessagingResponse()
    twilio_resp.message(respuesta_ia)
    return str(twilio_resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
