import os
import pymongo
import mysql.connector
from dotenv import load_dotenv

# Carrega o .env explicitamente pelo caminho do arquivo
load_dotenv(dotenv_path=".env")

print("\n=======================================================")
print("       RELATÓRIO DE PRONTIDÃO DO AMBIENTE (CP02)       ")
print("=======================================================")

# 1. Validação MongoDB
try:
    mongo_uri = os.getenv("MONGO_URI")
    mongo_client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
    mongo_client.admin.command("ping")
    print("✅ [MongoDB]: Operacional no contêiner 'mongo-lab' (porta 27017).")
except Exception as e:
    print(f"❌ [MongoDB]: Erro de conexão: {e}")

# 2. Validação MySQL
try:
    mysql_conn = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        connect_timeout=3
    )
    if mysql_conn.is_connected():
        print("✅ [MySQL]:   Operacional no contêiner 'mysql-lab' (porta 3306).")
        mysql_conn.close()
except Exception as e:
    print(f"❌ [MySQL]:   Erro de conexão: {e}")

# 3. Validação das bibliotecas científicas e web
try:
    import sklearn
    import flask
    import requests
    import numpy
    print("✅ [Pacotes]: scikit-learn, numpy, flask, requests validados.")
except ImportError as e:
    print(f"❌ [Pacotes]: Falha na importação: {e}")

print("=======================================================\n")
