import os
import sqlite3
import requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

# Configuración
app = Flask(__name__)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
DB_PATH = "reservas.db"

# Inicializar base de datos
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS reservas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT,
                        telefono TEXT,
                        fecha TEXT,
                        hora TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Función para procesar reservas con validación
def procesar_reserva(mensaje, telefono):
    palabras = mensaje.lower().split()
    
    if "reservar" in palabras:
        try:
            detalles = mensaje.replace("reservar", "").strip().split()
            
            # Validar que el usuario ha ingresado nombre, fecha y hora
            if len(detalles) < 3:
                return "Formato incorrecto. Usa: 'Reservar [nombre] [fecha en formato DD-MM-YYYY] [hora en formato HH:MM]'"

            nombre, fecha, hora = detalles[0], detalles[1], detalles[2]

            # Validar formato de fecha y hora
            if not validar_fecha_hora(fecha, hora):
                return "Formato incorrecto. Usa: 'Reservar [nombre] [fecha en formato DD-MM-YYYY] [hora en formato HH:MM]'"

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO reservas (nombre, telefono, fecha, hora) VALUES (?, ?, ?, ?)",
                           (nombre, telefono, fecha, hora))
            conn.commit()
            conn.close()

            return f"Reserva confirmada para {nombre} el {fecha} a las {hora}. Recibirás un recordatorio antes de tu cita."

        except Exception as e:
            return "Hubo un error al procesar la reserva. Asegúrate de seguir el formato correcto."

    return None

# Validar formato de fecha y hora
def validar_fecha_hora(fecha, hora):
    from datetime import datetime
    try:
        datetime.strptime(fecha, "%d-%m-%Y")  # Verifica formato de fecha
        datetime.strptime(hora, "%H:%M")  # Verifica formato de hora
        return True
    except ValueError:
        return False

# Función para interactuar con OpenRouter
def obtener_respuesta_openrouter(mensaje):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mistralai/mistral-7b-instruct:free",
        "messages": [{
            "role": "system",
            "content": "Eres un asistente virtual para el Centre d'Especialitats Mèdiques Betulo. Tu rol es actuar como la secretaria encargada de gestionar reservas de pacientes, responder dudas sobre ubicación y enviar recordatorios de citas. Cuando un paciente diga que quiere reservar, pídele su nombre completo, luego la fecha en formato dia-mes-año, y después la hora en formato hora:minuto. Confirma la cita con un mensaje claro como 'Tu cita ha sido confirmada para el dia-mes-año a las hora:minuto. Recibirás un recordatorio antes de la cita'. Guarda esta información correctamente en la base de datos. Si un paciente pregunta si tiene una cita programada, revisa en la base de datos y responde con los detalles. Un día antes de cada cita, envía un mensaje recordatorio como 'Hola nombre, te recordamos que tienes una cita mañana a las hora:minuto en nuestra clínica podológica'. También puedes responder preguntas frecuentes sobre la ubicación. La clínica está en Carrer de Guifré, 199, 08912 Badalona, Barcelona. Si un paciente necesita más información, puede llamar al teléfono 934642218. Mantén siempre un tono educado, profesional y amable, usa frases cortas y claras, y confirma la información recibida. Si el paciente escribe algo que no está relacionado con reservas o información de la clínica, responde con 'Lo siento, solo puedo ayudarte con reservas y consultas sobre la clínica. ¿Te gustaría agendar una cita?'. No des información médica ni diagnósticos, y mantén la conversación enfocada en la gestión de citas y dudas básicas de la clínica."
        },
        {"role": "user", "content": mensaje}]
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"] if response.status_code == 200 else "Error en la respuesta de IA."

# Ruta del webhook para Twilio
@app.route("/webhook", methods=["POST"])
def webhook():
    msg = request.form.get("Body")
    telefono = request.form.get("From")

    # Intentar procesar como reserva
    respuesta_reserva = procesar_reserva(msg, telefono)
    if respuesta_reserva:
        return str(MessagingResponse().message(respuesta_reserva))

    # Si no es una reserva, responder con IA
    respuesta_ia = obtener_respuesta_openrouter(msg)
    twilio_resp = MessagingResponse()
    twilio_resp.message(respuesta_ia)
    return str(twilio_resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
