import os
import requests
from flask import Flask, request
from twilio.rest import Client

app = Flask(__name__)

# 📌 Configuración de Twilio desde las variables de entorno
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

# 📌 URL del Webhook de BotPress (Cambia esto por tu URL real)
BOTPRESS_WEBHOOK_URL = "https://webhook.botpress.cloud/feb9baf2-5897-45c8-ac54-8bc62690687e"

client = Client(ACCOUNT_SID, AUTH_TOKEN)

@app.route("/", methods=["GET"])
def home():
    return "Webhook Flask Activo", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    """ Recibe mensajes de WhatsApp (Twilio) y los reenvía a BotPress. """
    
    data = request.form  # Captura los datos del mensaje de Twilio
    sender = data.get("From", "Desconocido")
    message_text = data.get("Body", "").lower()

    print(f"📩 Mensaje de {sender}: {message_text}")

    # 🔹 1. Enviar mensaje a BotPress
    botpress_payload = {
        "type": "text",
        "text": message_text,
        "from": sender
    }
    
    botpress_response = requests.post(BOTPRESS_WEBHOOK_URL, json=botpress_payload)
    
    if botpress_response.status_code == 200:
        bot_response = botpress_response.json().get("responses", [{"text": "No tengo respuesta para eso."}])[0]["text"]
    else:
        bot_response = "Error al conectar con BotPress."

    # 🔹 2. Enviar la respuesta de BotPress a WhatsApp (Twilio)
    send_whatsapp_message(sender, bot_response)

    return "EVENT_RECEIVED", 200

def send_whatsapp_message(recipient, message):
    """ Envía un mensaje de WhatsApp a través de Twilio. """
    
    url = f"https://api.twilio.com/2010-04-01/Accounts/{ACCOUNT_SID}/Messages.json"
    headers = {"Authorization": f"Basic {os.getenv('TWILIO_AUTH_BASE64')}"}
    payload = {
        "From": TWILIO_NUMBER,
        "To": recipient,
        "Body": message
    }
    
    response = requests.post(url, data=payload, headers=headers)
    print(f"📤 Respuesta enviada a {recipient}: {message}")
    print(f"🔄 Twilio Response: {response.status_code}, {response.text}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
