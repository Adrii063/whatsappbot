from flask import Flask, request

app = Flask(__name__)

# Token de verificación de Meta
VERIFY_TOKEN = "botpress123"

@app.route("/", methods=["GET"])
def home():
    return "Webhook Flask Activo", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge"), 200
        return "Error de verificación", 403

    if request.method == "POST":
        data = request.json
        print("Mensaje recibido:", data)
        return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
