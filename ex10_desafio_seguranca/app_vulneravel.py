"""Laboratório local propositalmente vulnerável; não expor em rede pública."""
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
    cur.execute("CREATE TABLE IF NOT EXISTS usuarios (id INT PRIMARY KEY,nome VARCHAR(60),email VARCHAR(100),senha VARCHAR(100),nivel_acesso INT)")
    cur.execute("SHOW COLUMNS FROM usuarios LIKE 'senha'")
    if not cur.fetchone():
        cur.execute("ALTER TABLE usuarios ADD COLUMN senha VARCHAR(100)")
    cur.execute("DELETE FROM usuarios")
    cur.executemany("INSERT INTO usuarios (id,nome,email,nivel_acesso) VALUES (%s,%s,%s,%s)", [(1, "ana", "ana@x.com", 5), (2, "bruno", "bruno@x.com", 2), (3, "caio", "caio@x.com", 1)])
    con.commit()
    con.close()


@app.get("/api/usuarios/buscar")
def buscar():
    nome = request.args.get("nome", "")
    con = db()
    cur = con.cursor(dictionary=True)
    cur.execute(f"SELECT * FROM usuarios WHERE nome LIKE '%{nome}%'")
    dados = cur.fetchall()
    con.close()
    return jsonify(dados)


@app.get("/perfil")
def perfil():
    return f"<h1>Bem-vindo, {request.args.get('u', '')}</h1>"


@app.delete("/api/usuarios/<int:uid>")
def remover(uid):
    con = db()
    cur = con.cursor()
    cur.execute("DELETE FROM usuarios WHERE id=%s", (uid,))
    con.commit()
    con.close()
    return jsonify(removido=uid)


@app.get("/api/relatorio")
def relatorio():
    con = db()
    cur = con.cursor()
    cur.execute("SELECT * FROM tabela_inexistente")
    return jsonify(cur.fetchall())


if __name__ == "__main__":
    preparar()
    app.run(port=5010, debug=True, use_reloader=False, host="127.0.0.1")
