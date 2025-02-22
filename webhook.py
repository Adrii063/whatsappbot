from flask import Flask, request

app = Flask(__name__)

# Token de verificación definido en Meta
VERIFY_TOKEN = "botpress123"

@app.route("/", methods=["GET"])
def home():
    return "Webhook Flask Activo"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Capturar los parámetros enviados por Meta
        verify_token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        
        if verify_token == VERIFY_TOKEN and challenge:
            return str(challenge), 200  # Devolver el challenge como string
        
        return "Error de verificación", 403

    if request.method == "POST":
        # Aquí procesaremos los eventos de WhatsApp
        data = request.json
        print("Mensaje recibido:", data)
        return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
