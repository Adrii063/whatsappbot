import os
import requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

# Configuración
app = Flask(__name__)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Función para interactuar con OpenRouter
def obtener_respuesta_openrouter(mensaje):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mistralai/mistral-7b-instruct:free",
        "messages": [{"role": "system", "content": "Eres un chatbot de WhatsApp."},
                     {"role": "user", "content": mensaje}]
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        print(f"Error en OpenRouter: {e}")
        return "Lo siento, no puedo responder en este momento."

# Ruta del webhook para Twilio
@app.route("/webhook", methods=["POST"])
def webhook():
    msg = request.form.get("Body")
    
    respuesta_ia = obtener_respuesta_openrouter(msg)
    twilio_resp = MessagingResponse()
    twilio_resp.message(respuesta_ia)
    return str(twilio_resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
