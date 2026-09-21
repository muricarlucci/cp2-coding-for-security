"""Versão corrigida do laboratório, para execução exclusivamente local."""
import html, logging, os
from dotenv import load_dotenv
import mysql.connector
from flask import Flask, jsonify, request
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"));app=Flask(__name__);logging.basicConfig(level=logging.INFO)
def db():return mysql.connector.connect(host=os.getenv("MYSQL_HOST"),port=int(os.getenv("MYSQL_PORT","3306")),user=os.getenv("MYSQL_USER"),password=os.getenv("MYSQL_PASSWORD"),database=os.getenv("MYSQL_DATABASE"))
def preparar():
    con=db();cur=con.cursor();cur.execute("CREATE TABLE IF NOT EXISTS usuarios (id INT PRIMARY KEY,nome VARCHAR(60),email VARCHAR(100),senha VARCHAR(100),nivel_acesso INT)")
    cur.execute("SHOW COLUMNS FROM usuarios LIKE 'senha'")
    if not cur.fetchone(): cur.execute("ALTER TABLE usuarios ADD COLUMN senha VARCHAR(100)")
    cur.execute("DELETE FROM usuarios");cur.executemany("INSERT INTO usuarios (id,nome,email,nivel_acesso) VALUES (%s,%s,%s,%s)",[(1,"ana","ana@x.com",5),(2,"bruno","bruno@x.com",2),(3,"caio","caio@x.com",1)]);con.commit();con.close()
@app.after_request
def headers(resposta):
    resposta.headers["Content-Security-Policy"]="default-src 'self'";resposta.headers["X-Content-Type-Options"]="nosniff";resposta.headers["X-Frame-Options"]="DENY";return resposta
@app.before_request
def registrar():logging.info("requisicao metodo=%s rota=%s",request.method,request.path)
@app.errorhandler(Exception)
def falha(erro):logging.exception("erro interno");return jsonify(erro="erro interno"),500
def admin():return request.headers.get("X-API-Key")==os.getenv("ADMIN_API_KEY")
@app.get("/api/usuarios/buscar")
def buscar():
    nome=request.args.get("nome","");con=db();cur=con.cursor(dictionary=True);cur.execute("SELECT id,nome,email,nivel_acesso FROM usuarios WHERE nome LIKE %s",(f"%{nome}%",));dados=cur.fetchall();con.close();return jsonify(dados)
@app.get("/perfil")
def perfil():return f"<h1>Bem-vindo, {html.escape(request.args.get('u',''),quote=True)}</h1>"
@app.delete("/api/usuarios/<int:uid>")
def remover(uid):
    if not request.headers.get("X-API-Key"):return jsonify(erro="não autenticado"),401
    if not admin():return jsonify(erro="acesso negado"),403
    con=db();cur=con.cursor();cur.execute("DELETE FROM usuarios WHERE id=%s",(uid,));con.commit();con.close();return jsonify(removido=uid)
@app.get("/api/relatorio")
def relatorio():raise RuntimeError("consulta indisponível")
if __name__=="__main__":preparar();app.run(port=5010,debug=False,host="127.0.0.1")
