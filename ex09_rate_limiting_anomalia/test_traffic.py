"""Cliente local: execute com o servidor do exercício 9 ativo."""
import requests

BASE="http://127.0.0.1:5009"


def chamar(ip, rota="/api/status"):
    return requests.get(BASE + rota, headers={"X-Forwarded-For": ip}, timeout=3)


if __name__ == "__main__":
    for _ in range(5):
        chamar("192.168.1.10")
    for i in range(60):
        chamar("185.220.101.1", "/api/status" if i >= 40 else f"/inexistente/{i}")

    print("=== Análise de acessos ===")
    for perfil in requests.get(BASE + "/api/analise", timeout=3).json():
        print(perfil)

    resposta = chamar("185.220.101.1")
    print("Próxima requisição hostil:", resposta.status_code, resposta.json(), "Retry-After:", resposta.headers.get("Retry-After"))
