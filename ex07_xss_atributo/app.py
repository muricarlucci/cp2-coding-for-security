"""Exercício 7 — Jinja2 escapa inclusive valores em atributos HTML."""
import os
from dotenv import load_dotenv
from flask import Flask, render_template
from pymongo import MongoClient
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env")); app=Flask(__name__)
def alertas(): return MongoClient(os.getenv("MONGO_URI"))[os.getenv("MYSQL_DATABASE")]["incidentes_xss"]
@app.after_request
def csp(resposta): resposta.headers["Content-Security-Policy"]="default-src 'self'"; return resposta
@app.get("/dashboard")
def dashboard(): return render_template("dashboard.html", alertas=list(alertas().find({}, {"_id":0})))
@app.get("/dashboard-inseguro")
def dashboard_inseguro(): return render_template("dashboard_inseguro.html", alertas=list(alertas().find({}, {"_id":0})))
def preparar():
    colecao=alertas();colecao.delete_many({});colecao.insert_many([{"titulo":"<script>alert('xss1')</script>","severidade":"alta"},{"titulo":"x\" onerror=\"alert('xss2')","severidade":"media"}])
if __name__=="__main__":preparar();app.run(port=5007,debug=False)
