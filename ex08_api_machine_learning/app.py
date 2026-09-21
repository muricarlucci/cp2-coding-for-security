"""Exercício 8 — modelo de triagem, validação de entrada e auditoria."""
import os
from datetime import datetime

import numpy as np
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from pymongo import MongoClient
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

app = Flask(__name__)

X = np.array([
    [0, 1, 900, 12], [1, 1, 1200, 14], [2, 2, 3000, 9],
    [12, 7, 90000, 3], [9, 8, 80000, 2], [15, 6, 110000, 1],
    [0, 1, 1000, 18], [3, 2, 4000, 11], [11, 9, 95000, 4],
    [1, 3, 2500, 20], [13, 7, 100000, 5], [2, 1, 1800, 15],
])
y = np.array([0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0])

Xtreino, Xteste, ytreino, yteste = train_test_split(
    X, y, test_size=.33, random_state=42, stratify=y
)
modelo = RandomForestClassifier(n_estimators=100, random_state=42).fit(Xtreino, ytreino)
previsto = modelo.predict(Xteste)


def previsoes():
    return MongoClient(os.getenv("MONGO_URI"))[os.getenv("MYSQL_DATABASE")]["previsoes"]


@app.post("/api/triagem")
def triagem():
    corpo = request.get_json(silent=True)
    if not isinstance(corpo, dict) or "features" not in corpo:
        return jsonify(erro="corpo JSON com features é obrigatório"), 400

    features = corpo["features"]
    if not isinstance(features, list) or len(features) != 4:
        recebidas = len(features) if isinstance(features, list) else 0
        return jsonify(erro=f"esperadas 4 features, recebidas {recebidas}"), 400
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) for x in features):
        return jsonify(erro="features devem ser numéricas"), 400

    classe = int(modelo.predict([features])[0])
    confianca = float(max(modelo.predict_proba([features])[0]))
    saida = {"risco": "alto" if classe else "baixo", "confianca": round(confianca, 2)}

    previsoes().insert_one({"entrada": features, "saida": saida["risco"], "confianca": saida["confianca"], "timestamp": datetime.now()})
    return jsonify(saida)


@app.get("/api/modelo/metricas")
def metricas():
    return jsonify(
        precisao=round(float(precision_score(yteste, previsto, zero_division=0)), 2),
        recall=round(float(recall_score(yteste, previsto, zero_division=0)), 2),
        f1=round(float(f1_score(yteste, previsto, zero_division=0)), 2),
        matriz=confusion_matrix(yteste, previsto).tolist(),
        aviso="A acurácia foi omitida: em SOC desbalanceado um modelo pode atingir 99% de acurácia e ainda ter 0% de recall para incidentes.",
    )


if __name__ == "__main__":
    app.run(port=5008, debug=False)
