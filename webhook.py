import os
from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Cargar credenciales desde variables de entorno
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")  # Número de Twilio

client = Client(ACCOUNT_SID, AUTH_TOKEN)

@app.route("/", methods=["GET"])
def home():
    return "Webhook Flask Activo", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return "Webhook funcionando correctamente", 200

    if request.method == "POST":
        data = request.form
        sender = data.get("From", "Desconocido")
        message = data.get("Body", "").lower()

        print(f"Mensaje de {sender}: {message}")

        # Crear respuesta automática
        response = MessagingResponse()
        response.message(f"Hola, recibí tu mensaje: '{message}'. ¿En qué puedo ayudarte?")

        return str(response), 200  # Enviar respuesta en formato TwiML

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
