"""Exercício 2 — migração MySQL para documentos MongoDB."""
import os
from dotenv import load_dotenv
import mysql.connector
from pymongo import MongoClient

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

def mysql_conexao():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
    )

def main():
    con = mysql_conexao()
    cur = con.cursor(dictionary=True)
    cur.execute("CREATE TABLE IF NOT EXISTS ativos (id INT PRIMARY KEY, nome VARCHAR(60), ip VARCHAR(45) UNIQUE, criticidade ENUM('baixa','media','alta'))")
    cur.execute("CREATE TABLE IF NOT EXISTS alertas (id INT PRIMARY KEY, ativo_id INT, tipo VARCHAR(60), severidade VARCHAR(20), criado_em DATETIME, FOREIGN KEY (ativo_id) REFERENCES ativos(id))")
    cur.execute("DELETE FROM alertas")
    cur.execute("DELETE FROM ativos")
    cur.executemany("INSERT INTO ativos (id,nome,ip,criticidade) VALUES (%s,%s,%s,%s)", [(1, "SRV-WEB01", "192.168.1.10", "alta"), (2, "PC-RH03", "192.168.1.45", "baixa")])
    cur.executemany("INSERT INTO alertas (id,ativo_id,tipo,severidade,criado_em) VALUES (%s,%s,%s,%s,NOW())", [(1, 1, "BRUTE_FORCE", "critica"), (2, 1, "PORT_SCAN", "alta"), (3, 2, "XSS", "media")])
    con.commit()
    cur.execute("SELECT a.tipo,a.severidade,t.nome,t.ip,t.criticidade FROM alertas a JOIN ativos t ON t.id=a.ativo_id WHERE a.id >= %s", (0,))
    docs = [{"tipo": r["tipo"], "severidade": r["severidade"], "ativo": {"nome": r["nome"], "ip": r["ip"], "criticidade": r["criticidade"]}} for r in cur.fetchall()]
    colecao = MongoClient(os.getenv("MONGO_URI"))[os.getenv("MYSQL_DATABASE")]["alertas"]
    colecao.delete_many({}); colecao.insert_many(docs)
    cur.execute("SELECT COUNT(*) AS total FROM alertas")
    mysql_total = cur.fetchone()["total"]
    mongo_total = colecao.count_documents({})
    print(f"MySQL: {mysql_total} alertas | MongoDB: {mongo_total} documentos ->", "MIGRAÇÃO ÍNTEGRA" if mysql_total == mongo_total else "FALHOU")
    print('Consulta sem JOIN: db.alertas.find({"ativo.criticidade":"alta"}) ->', colecao.count_documents({"ativo.criticidade":"alta"}), "documentos")
    # A leitura analítica é rápida porque o documento já traz o ativo, sem JOIN.
    # Há duplicação: renomear o ativo exige update_many nos alertas correspondentes.
    con.close()

if __name__ == "__main__":
    main()
