from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = "botpress123"

@app.route("/", methods=["GET"])
def home():
    return "Webhook Flask Activo"

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if token == VERIFY_TOKEN:
        return challenge, 200  # Meta espera recibir este valor exacto
    return "Token inválido", 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)  # 🔹 IMPORTANTE: host="0.0.0.0"