"""Exercício 1 — decisão de armazenamento fundamentada em risco."""

def recomendar(perfil):
    """Escolhe banco/CAP a partir das propriedades de segurança do dado."""
    if perfil["precisa_acid"] or not perfil["tolera_atraso_de_consistencia"]:
        banco, cap = ("MySQL", "CP") if perfil["schema_fixo"] else ("MongoDB", "CP")
        if perfil["precisa_acid"]:
            justificativa = "aceitar uma alteração parcial de permissão ou autenticar errado é pior que ficar temporariamente fora do ar"
            risco = "A07 — Falhas de Identificação e Autenticação"
        elif perfil["dado_sensivel"]:
            justificativa = "uma trilha de auditoria divergente não serve como prova de uma ação sensível"
            risco = "A08 — Falhas de Integridade de Software e Dados"
        else:
            justificativa = "entregar um estado divergente ao usuário é pior que recusar a operação durante a partição"
            risco = "A04 — Falhas de Design Inseguro"
    else:
        banco, cap = "MongoDB", "AP"
        justificativa = "perder alguns segundos de telemetria é menos grave que parar de aceitar novos eventos durante uma falha de rede"
        risco = "A09 — Falhas de Registro e Monitoramento de Segurança"
    return {"banco": banco, "cap": cap, "justificativa": justificativa, "risco_owasp": risco}


if __name__ == "__main__":
    perfis = {
        "credenciais_do_SOC": {"schema_fixo": True, "precisa_acid": True, "escala_horizontal": False, "tolera_atraso_de_consistencia": False, "dado_sensivel": True},
        "telemetria_de_sensores": {"schema_fixo": False, "precisa_acid": False, "escala_horizontal": True, "tolera_atraso_de_consistencia": True, "dado_sensivel": False},
        "trilha_de_auditoria": {"schema_fixo": False, "precisa_acid": False, "escala_horizontal": True, "tolera_atraso_de_consistencia": False, "dado_sensivel": True},
    }
    for nome, perfil in perfis.items():
        print(nome, "->", recomendar(perfil))
