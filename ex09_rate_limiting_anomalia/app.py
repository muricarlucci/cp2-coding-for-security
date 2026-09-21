"""Exercício 9 — telemetria MongoDB e bloqueio por IsolationForest."""
import os
from datetime import datetime, timedelta
import numpy as np
from dotenv import load_dotenv
from flask import Flask, g, jsonify, request
from pymongo import MongoClient
from sklearn.ensemble import IsolationForest
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"));app=Flask(__name__); bloqueados=set()
def acessos():return MongoClient(os.getenv("MONGO_URI"))[os.getenv("MYSQL_DATABASE")]["acessos"]
def ip_cliente():return request.headers.get("X-Forwarded-For",request.remote_addr).split(",")[0].strip()
@app.before_request
def registrar():
    g.acesso_id=acessos().insert_one({"ip":ip_cliente(),"rota":request.path,"metodo":request.method,"timestamp":datetime.now()}).inserted_id
    if ip_cliente() in bloqueados:return jsonify(erro="muitas requisições"),429,{"Retry-After":"60"}
@app.after_request
def completar(resposta):
    if hasattr(g,"acesso_id"):acessos().update_one({"_id":g.acesso_id},{"$set":{"status_code":resposta.status_code}})
    return resposta
@app.get("/api/status")
def status():return jsonify(status="ok")
@app.get("/api/analise")
def analise():
    janela=datetime.now()-timedelta(minutes=1)
    pipeline=[{"$match":{"timestamp":{"$gte":janela}}},{"$group":{"_id":"$ip","req_por_minuto":{"$sum":1},"erros":{"$sum":{"$cond":[{"$gte":["$status_code",400]},1,0]}},"rotas":{"$addToSet":"$rota"}}}]
    perfis=list(acessos().aggregate(pipeline));
    if len(perfis)>=2:
        dados=np.array([[p["req_por_minuto"],p["erros"]/p["req_por_minuto"],len(p["rotas"])] for p in perfis])
        # Perfis benignos de referência evitam que uma janela com só dois IPs torne o modelo cego ao outlier.
        referencia=np.array([[3,.0,1],[5,.0,2],[7,.05,2],[4,.0,1],[6,.0,2]])
        detector=IsolationForest(contamination=0.2,random_state=42).fit(np.vstack((referencia,dados)))
        previsao=detector.predict(dados)
        for p,marca in zip(perfis,previsao):
            if marca==-1:bloqueados.add(p["_id"])
    saida=[{"ip":p["_id"],"req_por_minuto":p["req_por_minuto"],"taxa_4xx":round(p["erros"]/p["req_por_minuto"],2),"rotas_distintas":len(p["rotas"]),"classificacao":"ANOMALIA" if p["_id"] in bloqueados else "normal"} for p in perfis]
    return jsonify(saida)
# Um falso positivo pode bloquear um usuário legítimo atrás de um NAT corporativo compartilhado.
# A anomalia estatística deve ter expiração, revisão humana e não ser a única evidência.
if __name__=="__main__":app.run(port=5009,debug=False)
