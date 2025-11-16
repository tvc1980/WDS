from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("temperaturas.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS temperatura (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        valor REAL NOT NULL,
        data_hora TEXT NOT NULL
    )""")
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/temperatura", methods=["POST"])
def receber_temperatura():
    data = request.get_json()
    valor = float(data.get("temperatura"))

    # Ajuste de fuso horário para Brasil (UTC-3)
    FUSO_BR = timedelta(hours=-3)
    horario_br = datetime.utcnow() + FUSO_BR

    # Formato desejado: (YYYY-MM-DD) HH:MM:SS
    data_formatada = horario_br.strftime("(%Y-%m-%d) %H:%M:%S")

    conn = sqlite3.connect("temperaturas.db")
    c = conn.cursor()
    c.execute("INSERT INTO temperatura (valor, data_hora) VALUES (?, ?)",
              (valor, data_formatada))
    conn.commit()
    conn.close()

    print(f"Temperatura recebida: {valor}°C às {data_formatada}")
    return jsonify({"status": "ok"}), 200

@app.route("/historico")
def historico():
    conn = sqlite3.connect("temperaturas.db")
    c = conn.cursor()
    c.execute("SELECT valor, data_hora FROM temperatura ORDER BY id DESC LIMIT 100")
    dados = c.fetchall()
    conn.close()

    valores = [d[0] for d in dados][::-1]
    datas = [d[1] for d in dados][::-1]

    return jsonify({"temperatura": valores, "tempo": datas})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
