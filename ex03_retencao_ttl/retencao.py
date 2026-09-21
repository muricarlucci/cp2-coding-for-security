"""Exercício 3 — TTL e agregação temporal no MongoDB."""
import os, random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pymongo import MongoClient
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

def main():
    eventos = MongoClient(os.getenv("MONGO_URI"))[os.getenv("MYSQL_DATABASE")]["eventos"]
    eventos.create_index("timestamp", expireAfterSeconds=604800)
    eventos.delete_many({})
    agora = datetime.now()
    eventos.insert_many([{ "tipo": "falha_login", "timestamp": agora - timedelta(minutes=random.randint(0, 1439))} for _ in range(200)])
    dados = list(eventos.aggregate([{"$match": {"timestamp": {"$gte": agora - timedelta(hours=24)}}}, {"$group": {"_id": {"$hour": "$timestamp"}, "total": {"$sum": 1}}}, {"$sort": {"_id": 1}}]))
    pico = max(dados, key=lambda item: item["total"])
    print("=== Falhas por hora (últimas 24h) ===")
    for item in dados: print(f'{item["_id"]:02}h | ' + "█" * item["total"] + f' {item["total"]}' + (" <- pico" if item == pico else ""))
    print(f'Hora de pico: {pico["_id"]:02}h ({pico["total"]} falhas)')
    print("Índice TTL ativo: eventos com mais de 7 dias serão removidos automaticamente.")
    # TTL reduz a superfície de exposição ao descartar dados sensíveis quando deixam de ser necessários.
if __name__ == "__main__": main()
