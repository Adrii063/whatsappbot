from flask import Flask, request, jsonify
import requests
import os
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

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
    
    # 👇 Agregamos prints para debuggear
    print("STATUS CODE:", response.status_code)
    print("RESPONSE TEXT:", response.text)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error en OpenRouter: {response.text}"


@app.route("/webhook", methods=["POST"])
def webhook():
    mensaje_usuario = request.form.get("Body")

    if not mensaje_usuario:
        return "No se recibió mensaje"

    respuesta_ia = obtener_respuesta_ia(mensaje_usuario)

    # 🟢 Aquí aseguramos que la respuesta sea un TwiML válido para Twilio
    twilio_resp = MessagingResponse()
    twilio_resp.message(respuesta_ia)

    return str(twilio_resp)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
