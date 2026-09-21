"""Exercício 4 — transação MySQL com auditoria incondicional no MongoDB."""
import os
from datetime import datetime

import mysql.connector
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


def conexao():
    return mysql.connector.connect(host=os.getenv("MYSQL_HOST"), port=int(os.getenv("MYSQL_PORT", "3306")), user=os.getenv("MYSQL_USER"), password=os.getenv("MYSQL_PASSWORD"), database=os.getenv("MYSQL_DATABASE"))


def auditoria():
    return MongoClient(os.getenv("MONGO_URI"))[os.getenv("MYSQL_DATABASE")]["auditoria"]


def alterar_nivel(admin_id, alvo_id, novo_nivel):
    con = conexao()
    cur = con.cursor(dictionary=True)
    anterior = None
    resultado = "RECUSADO"

    try:
        cur.execute("SELECT nivel_acesso FROM usuarios WHERE id = %s", (admin_id,))
        admin = cur.fetchone()
        cur.execute("SELECT nivel_acesso FROM usuarios WHERE id = %s", (alvo_id,))
        alvo = cur.fetchone()
        anterior = alvo["nivel_acesso"] if alvo else None

        if not admin or admin["nivel_acesso"] < 5:
            raise PermissionError("admin sem privilégio")
        if admin_id == alvo_id:
            raise PermissionError("auto-promoção proibida")
        if not alvo:
            raise LookupError("alvo inexistente")

        cur.execute("UPDATE usuarios SET nivel_acesso = %s WHERE id = %s", (novo_nivel, alvo_id))
        con.commit()
        resultado = "OK"
    except (PermissionError, LookupError) as erro:
        con.rollback()
        print("RECUSADO:", erro)
    except Exception:
        con.rollback()
        raise
    finally:
        auditoria().insert_one({"quem": admin_id, "alvo": alvo_id, "nivel_anterior": anterior, "nivel_novo": novo_nivel, "resultado": resultado, "timestamp": datetime.now()})
        cur.close()
        con.close()

    return resultado


def preparar():
    con = conexao()
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS usuarios (id INT PRIMARY KEY, nome VARCHAR(60), email VARCHAR(100), nivel_acesso INT)")
    cur.execute("DELETE FROM usuarios")
    cur.executemany("INSERT INTO usuarios (id,nome,email,nivel_acesso) VALUES (%s,%s,%s,%s)", [(1, "ana", "ana@x.com", 5), (2, "bruno", "bruno@x.com", 2), (3, "caio", "caio@x.com", 1)])
    con.commit()
    con.close()
    auditoria().delete_many({})


if __name__ == "__main__":
    preparar()
    for args in [(1, 2, 4), (2, 3, 5), (1, 1, 9), (1, 99, 3)]:
        print(args, "->", alterar_nivel(*args))
    print("Recusas:", auditoria().count_documents({"resultado": "RECUSADO"}))
