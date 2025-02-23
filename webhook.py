from flask import Flask, request

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Webhook Flask Activo", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return "Webhook funcionando correctamente", 200

    if request.method == "POST":
        data = request.form  # Cambiado de request.json a request.form
        print("Mensaje recibido:", data)
        
        # Extraer datos de Twilio
        sender = data.get("From", "Desconocido")
        message = data.get("Body", "Sin mensaje")
        
        print(f"Mensaje de {sender}: {message}")

        return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
