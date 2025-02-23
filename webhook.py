from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
import os

app = Flask(__name__)

# Credenciales (usa variables de entorno en Render)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# URL de OpenRouter
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Función para obtener respuesta de la IA
def obtener_respuesta_ia(mensaje):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "mistralai/mistral-7b-instruct:free",
        "messages": [
            {"role": "system", "content": "Eres un chatbot de WhatsApp."},
            {"role": "user", "content": mensaje}
        ]
    }

    response = requests.post(OPENROUTER_URL, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return "Lo siento, no pude procesar tu solicitud en este momento."

# Webhook para recibir mensajes de WhatsApp
@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.values.get("Body", "").strip()
    resp = MessagingResponse()
    msg = resp.message()

    if incoming_msg:
        respuesta = obtener_respuesta_ia(incoming_msg)
        msg.body(respuesta)
    else:
        msg.body("No entendí tu mensaje, intenta de nuevo.")

    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
