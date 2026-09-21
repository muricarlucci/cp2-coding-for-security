"""Exercício 5 — ORDER BY seguro somente por whitelist."""
import os
from datetime import datetime, timedelta

import mysql.connector
from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

app = Flask(__name__)
COLUNAS = {"data": "criado_em", "sev": "severidade", "ip": "ip_origem"}
ORDEM = {"asc": "ASC", "desc": "DESC"}


def db():
    return mysql.connector.connect(host=os.getenv("MYSQL_HOST"), port=int(os.getenv("MYSQL_PORT", "3306")), user=os.getenv("MYSQL_USER"), password=os.getenv("MYSQL_PASSWORD"), database=os.getenv("MYSQL_DATABASE"))


def preparar():
    con = db()
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS eventos_api (id INT AUTO_INCREMENT PRIMARY KEY, criado_em DATETIME, severidade VARCHAR(20), ip_origem VARCHAR(45))")
    cur.execute("DELETE FROM eventos_api")
    dados = [(datetime.now() - timedelta(minutes=i), ["baixa", "media", "alta", "critica"][i % 4], f"10.0.0.{i % 8}") for i in range(120)]
    cur.executemany("INSERT INTO eventos_api (criado_em,severidade,ip_origem) VALUES (%s,%s,%s)", dados)
    con.commit()
    con.close()


@app.get("/api/eventos")
def eventos():
    coluna = COLUNAS.get(request.args.get("ordenar_por", "data"))
    ordem = ORDEM.get(request.args.get("ordem", "asc").lower())
    if not coluna or not ordem:
        return jsonify(erro="campo de ordenação inválido"), 400

    try:
        tamanho = int(request.args.get("tamanho", "20"))
    except ValueError:
        return jsonify(erro="tamanho deve ser inteiro"), 400

    if tamanho < 1:
        return jsonify(erro="tamanho deve ser positivo"), 400

    # LIMIT %s funciona porque o driver o trata como valor literal de dado.
    # ORDER BY %s exige um identificador de schema, como nome de coluna, não um dado.
    # Por isso os identificadores vêm somente dos mapas fechados acima, nunca do cliente.
    con = db()
    cur = con.cursor(dictionary=True)
    cur.execute(f"SELECT criado_em,severidade,ip_origem FROM eventos_api ORDER BY {coluna} {ordem} LIMIT %s", (min(tamanho, 100),))
    dados = cur.fetchall()
    con.close()
    return jsonify(dados)


if __name__ == "__main__":
    preparar()
    app.run(port=5005, debug=False)
