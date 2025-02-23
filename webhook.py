import os
import requests
from flask import Flask, request
from twilio.rest import Client

app = Flask(__name__)

# Configuración de Twilio
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

# Configuración de OpenRouter
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Clave de OpenRouter
OPENROUTER_URL = "https://openrouter.ai/api/v1"
MODEL = "mistralai/mistral-7b-instruct:free"  # Modelo seleccionado

client_twilio = Client(ACCOUNT_SID, AUTH_TOKEN)

@app.route("/", methods=["GET"])
def home():
    return "Webhook Flask Activo", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    """ Recibe mensajes de WhatsApp, los reenvía a OpenRouter y devuelve la respuesta. """
    data = request.form
    sender = data.get("From", "Desconocido")
    message_text = data.get("Body", "").lower()

    print(f"📩 Mensaje de {sender}: {message_text}")

    # 🔹 1. Enviar mensaje a OpenRouter (Mistral) para obtener una respuesta
    bot_response = get_ai_response(message_text)

    # 🔹 2. Enviar la respuesta a WhatsApp
    send_whatsapp_message(sender, bot_response)

    return "EVENT_RECEIVED", 200

def get_ai_response(user_input):
    """ Envía el mensaje a OpenRouter (Mistral) y devuelve la respuesta. """
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "Eres un asistente de WhatsApp para restaurantes. Responde de manera breve, clara y educada."},
                {"role": "user", "content": user_input}
            ]
        }
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
        response_json = response.json()

        return response_json["choices"][0]["message"]["content"].strip()

    except Exception as e:
        print(f"❌ Error con OpenRouter: {e}")
        return "Lo siento, hubo un error al procesar tu solicitud."

def send_whatsapp_message(recipient, message):
    """ Envía un mensaje de WhatsApp a través de Twilio. """
    url = f"https://api.twilio.com/2010-04-01/Accounts/{ACCOUNT_SID}/Messages.json"
    payload = {
        "From": TWILIO_NUMBER,
        "To": recipient,
        "Body": message
    }

    response = requests.post(url, data=payload, auth=(ACCOUNT_SID, AUTH_TOKEN))
    print(f"📤 Respuesta enviada a {recipient}: {message}")
    print(f"🔄 Twilio Response: {response.status_code}, {response.text}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
