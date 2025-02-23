import os
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Obtener la API Key desde las variables de entorno
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Verificar que la clave esté configurada
if not OPENROUTER_API_KEY:
    raise ValueError("ERROR: La variable de entorno OPENROUTER_API_KEY no está configurada.")

# Ruta del webhook para Twilio
@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.form.get("Body")  # Mensaje recibido de WhatsApp
    sender = request.form.get("From")  # Número del remitente

    if not incoming_msg:
        return jsonify({"error": "No se recibió ningún mensaje."})

    # Llamar a la API de OpenRouter
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "mistralai/mistral-7b-instruct:free",
                "messages": [
                    {"role": "system", "content": "Eres un asistente amigable y útil en WhatsApp. Responde de manera clara y concisa."},
                    {"role": "user", "content": incoming_msg}
                ]
            }
        )

        if response.status_code != 200:
            return jsonify({"error": f"Error en OpenRouter: {response.status_code}", "details": response.text})

        data = response.json()
        reply = data["choices"][0]["message"]["content"]

    except Exception as e:
        return jsonify({"error": "Error procesando la solicitud.", "details": str(e)})

    # Respuesta a Twilio en formato XML
    return f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Message>{reply}</Message>
    </Response>"""

# Ejecutar la aplicación
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
