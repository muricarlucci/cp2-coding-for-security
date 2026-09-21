"""Exercício 6 — autenticação e autorização sem IDOR."""
import os

import mysql.connector
from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
app = Flask(__name__)


def db():
    return mysql.connector.connect(host=os.getenv("MYSQL_HOST"), port=int(os.getenv("MYSQL_PORT", "3306")), user=os.getenv("MYSQL_USER"), password=os.getenv("MYSQL_PASSWORD"), database=os.getenv("MYSQL_DATABASE"))


def preparar():
    con = db()
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS analistas (id INT PRIMARY KEY,nome VARCHAR(50),api_key VARCHAR(80) UNIQUE,nivel INT)")
    cur.execute("CREATE TABLE IF NOT EXISTS incidentes (id INT PRIMARY KEY,dono_id INT,titulo VARCHAR(120),severidade VARCHAR(20),status VARCHAR(20))")
    cur.execute("DELETE FROM incidentes")
    cur.execute("DELETE FROM analistas")
    cur.executemany("INSERT INTO analistas VALUES (%s,%s,%s,%s)", [(1, "ana", "key-ana-001", 5), (2, "bruno", "key-bruno-002", 2)])
    cur.executemany("INSERT INTO incidentes VALUES (%s,%s,%s,%s,%s)", [(1, 1, "Brute force SSH", "critica", "aberto"), (2, 2, "Phishing no RH", "media", "aberto")])
    con.commit()
    con.close()


def identidade():
    chave = request.headers.get("X-API-Key")
    if not chave:
        return None
    con = db()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT id,nivel FROM analistas WHERE api_key=%s", (chave,))
    analista = cur.fetchone()
    con.close()
    return analista


def erro_auth():
    return jsonify(erro="não autenticado"), 401


@app.get("/api/incidentes")
def listar():
    pessoa = identidade()
    if not pessoa:
        return erro_auth()
    con = db()
    cur = con.cursor(dictionary=True)
    if pessoa["nivel"] < 5:
        cur.execute("SELECT id,titulo,severidade,status FROM incidentes WHERE dono_id=%s", (pessoa["id"],))
    else:
        cur.execute("SELECT id,titulo,severidade,status FROM incidentes")
    dados = cur.fetchall()
    con.close()
    return jsonify(dados)


@app.route("/api/incidentes/<int:incidente_id>", methods=["GET", "DELETE"])
def incidente(incidente_id):
    pessoa = identidade()
    if not pessoa:
        return erro_auth()
    con = db()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM incidentes WHERE id=%s", (incidente_id,))
    item = cur.fetchone()
    if request.method == "GET":
        if not item:
            con.close()
            return jsonify(erro="incidente não encontrado"), 404
        if pessoa["nivel"] < 5 and item["dono_id"] != pessoa["id"]:
            con.close()
            return jsonify(erro="acesso negado"), 403
        con.close()
        return jsonify({k: item[k] for k in ("id", "titulo", "severidade", "status")})
    if pessoa["nivel"] < 5:
        con.close()
        return jsonify(erro="acesso negado"), 403
    if not item:
        con.close()
        return jsonify(erro="incidente não encontrado"), 404
    cur.execute("DELETE FROM incidentes WHERE id=%s", (incidente_id,))
    con.commit()
    con.close()
    return jsonify(removido=incidente_id)


if __name__ == "__main__":
    preparar()
    app.run(port=5006, debug=False)
