# Check Point 02 — Coding for Security (2º Semestre)

**Aluno:** Murilo Carlucci  
**Curso:** Cybersecurity — FIAP  
**Disciplina:** Coding for Security  
**Conteúdo Avaliado:** Aulas 1 a 8 (SQL vs NoSQL, PyMongo, MySQL, Machine Learning, APIs Flask e OWASP Top 10:2025)

---

## 📌 Visão Geral do Projeto

Este repositório contém a resolução prática e auditada dos 10 exercícios propostos no Check Point 02. O projeto consolida o desenvolvimento de microsserviços seguros em Python, persistência híbrida (relacional e documental), pipelines de Machine Learning defensivo e aplicação rigorosa das diretrizes do OWASP Top 10 (2025).

Todas as credenciais de banco e configurações sensíveis foram desacopladas em variáveis de ambiente via arquivo `.env`, garantindo conformidade estrita com a regra de proteção de segredos da avaliação.

---

## 🛠️ Ambiente e Pré-requisitos

O ambiente foi projetado para rodar sobre contêineres Docker, garantindo paridade com os laboratórios da disciplina.

### 1. Subir os Bancos de Dados (Docker)

Caso os contêineres do laboratório não estejam ativos, inicialize-os com os comandos oficiais da apostila:

```bash
# MongoDB 7 (Coleções analíticas e auditoria)
docker run -d --name mongo-lab -p 27017:27017 mongo:7

# MySQL 8 (Base relacional e controle de acesso)
docker run -d --name mysql-lab -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=senha \
  -e MYSQL_DATABASE=seguranca \
  mysql:8
```

### 2. Configurar o Ambiente Python

Recomenda-se o uso de ambiente virtual (`venv`):

```bash
# Criar e ativar o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate

# Instalar as dependências do semestre
pip install -r requirements.txt
```

### 3. Configurar Variáveis de Ambiente

Copie o arquivo de exemplo e ajuste se necessário (o padrão já aponta para os contêineres locais):

```bash
cp .env.example .env
```

---

## 📂 Mapa do Repositório e Execução dos Exercícios

Para evitar conflitos de porta durante a avaliação das APIs Flask, cada serviço foi configurado em uma porta TCP distinta (da `5005` à `5010`).

| Exercício | Diretório | Descrição / Tópico | Porta / Execução |
| :--- | :--- | :--- | :--- |
| **Ex 01** | `ex01_decisao_cap/` | Assistente de Decisão CAP e Riscos OWASP | `python ex01_decisao_cap/recomendador.py` |
| **Ex 02** | `ex02_migracao/` | Migração Normalizada (MySQL) $\rightarrow$ Documentos (Mongo) | `python ex02_migracao/migracao.py` |
| **Ex 03** | `ex03_retencao_ttl/` | Retenção com TTL Index e Agregação Temporal | `python ex03_retencao_ttl/retencao.py` |
| **Ex 04** | `ex04_transacao_auditoria/` | Transação ACID (MySQL) + Auditoria Ativa (Mongo) | `python ex04_transacao_auditoria/transacao.py` |
| **Ex 05** | `ex05_order_by_whitelist/` | Proteção de SQLi em `ORDER BY` via Whitelist | Porta `5005` (`app.py`) |
| **Ex 06** | `ex06_broken_access_control/` | Controle de Acesso (IDOR) e Autenticação por API Key | Porta `5006` (`app.py`) |
| **Ex 07** | `ex07_xss_atributo/` | Defesa contra XSS em atributos HTML e CSP | Porta `5007` (`app.py`) |
| **Ex 08** | `ex08_api_machine_learning/` | Triagem de Risco via Random Forest e Auditoria | Porta `5008` (`app.py`) |
| **Ex 09** | `ex09_rate_limiting_anomalia/` | Rate Limiting Dinâmico via Isolation Forest | Porta `5009` (`app.py` + `test_traffic.py`) |
| **Ex 10** | `ex10_desafio_seguranca/` | Auditoria Completa: Exploração vs Versão Hardened | Porta `5010` (`exploit.py`) |

---

## 🔍 Detalhamento das Soluções Implementadas

### Exercício 1 — Assistente de Decisão de Armazenamento
* **Arquivo:** `ex01_decisao_cap/recomendador.py`
* **Implementação:** A função `recomendar(perfil)` analisa as necessidades de consistência, esquema e escala para indicar MySQL ou MongoDB sob o prisma do Teorema CAP (CP vs AP).
* **Segurança:** As justificativas conectam a escolha tecnológica ao impacto operacional real caso haja falha (ex.: falha de consistência em autenticação permite acessos indevidos / OWASP A07; falta de disponibilidade em telemetria cega o monitoramento / OWASP A09).

### Exercício 2 — Migração Relacional $\rightarrow$ Documentos
* **Arquivo:** `ex02_migracao/migracao.py`
* **Implementação:** Realiza o `JOIN` parametrizado entre as tabelas `ativos` e `alertas` no MySQL e insere os documentos aninhados na coleção `alertas` do MongoDB via `insert_many`.
* **Validação:** Compara as contagens de registros em ambos os bancos para comprovar integridade e executa busca analítica sem `JOIN`.
* **Trade-off Técnico:** Ganha-se velocidade extrema em leitura analítica (sem custo de processamento de junções relacionais), mas perde-se em normalização (renomeações ou correções de ativos passam a exigir `update_many` concorrente).

### Exercício 3 — Retenção e Janela Temporal
* **Arquivo:** `ex03_retencao_ttl/retencao.py`
* **Implementação:** Configuração de índice TTL de 7 dias (`604800` segundos) sobre o campo `timestamp` e geração de 200 eventos espalhados nas últimas 24 horas. Agregação em pipeline com `$group` por `$hour` para traçar histograma em ASCII no terminal com identificação do pico.
* **Segurança:** O TTL é um controle ativo de segurança (princípio da minimização de dados e LGPD), reduzindo a janela de exposição de informações em caso de comprometimento da base.

### Exercício 4 — Transação com Trilha de Auditoria
* **Arquivo:** `ex04_transacao_auditoria/transacao.py`
* **Implementação:** Função `alterar_nivel(admin_id, alvo_id, novo_nivel)` com controle transacional estrito no MySQL (`commit` para sucessos e `rollback` para violações).
* **Defesa (OWASP A09):** Barrar auto-promoção ou operações de analistas com privilégio insuficiente dispara `rollback` imediato, mas **sempre** gera um documento de log na coleção `auditoria` do MongoDB. Violações de acesso precisam ser registradas para análise forense.

### Exercício 5 — O ORDER BY que o `%s` não protege
* **Arquivo:** `ex05_order_by_whitelist/app.py`
* **Porta:** `5005`
* **Implementação:** Endpoint `GET /api/eventos?ordenar_por=&ordem=&tamanho=`.
* **Segurança:** Drivers SQL tratam o placeholder `%s` como dado literal (escapado com aspas), o que corrompe a sintaxe se usado em identificadores de coluna ou cláusulas (`ORDER BY 'coluna'`). A aplicação implementa defesa por **whitelist** estrita. Tentativas de injeção retornam `400 Bad Request` semântico, com teto fixo de 100 registros para evitar DoS por consumo de memória.

### Exercício 6 — Controle de Acesso Quebrado
* **Arquivo:** `ex06_broken_access_control/app.py`
* **Porta:** `5006`
* **Implementação:** API de incidentes autenticada via cabeçalho `X-API-Key` contra tabela do MySQL.
* **Semântica de Segurança (IDOR):**
  * `401 Unauthorized`: Ausência de header ou chave não cadastrada.
  * `403 Forbidden`: Chave válida, mas o analista tenta visualizar incidente de outro analista ou usuário com nível $< 5$ tenta deletar registros. O corpo da resposta não vaza a existência prévia do ID.
  * `404 Not Found`: Apenas quando o usuário possui autorização, mas o recurso não existe.

### Exercício 7 — Defesa contra XSS em Atributos HTML
* **Arquivo:** `ex07_xss_atributo/app.py`
* **Porta:** `5007`
* **Implementação:** Rota `/dashboard` consumindo dados do MongoDB e renderizando template Jinja2 seguro, incluindo o título dentro do atributo `alt` de uma tag `<img>`.
* **Defesa:** O escape contextual padrão do Jinja2 impede que o payload `x" onerror="alert('xss2')` quebre o delimitador do atributo. Adicionalmente, foi aplicado o cabeçalho `Content-Security-Policy: default-src 'self'` via middleware `@app.after_request`. A rota `/dashboard-inseguro` foi mantida para análise comparativa.

### Exercício 8 — Modelo de ML com Auditoria
* **Arquivo:** `ex08_api_machine_learning/app.py`
* **Porta:** `5008`
* **Implementação:** Treinamento de `RandomForestClassifier` com `random_state=42` sobre 4 features comportamentais.
* **Rotas:** `POST /api/triagem` (valida estritamente tamanho e tipagem das features, persistindo predições válidas no MongoDB) e `GET /api/modelo/metricas` (retorna precision, recall, F1 e matriz de confusão).
* **Nota sobre Acurácia:** O retorno inclui justificativa explícita documentando por que a acurácia foi omitida: em cenários de segurança com classes desbalanceadas (ataques raros em meio a tráfego volumoso), a acurácia é uma métrica ilusória.

### Exercício 9 — Rate Limiting Guiado por Anomalia
* **Arquivos:** `ex09_rate_limiting_anomalia/app.py` e `test_traffic.py`
* **Porta:** `5009`
* **Implementação:** Middleware registra telemetria de requisições na coleção `acessos` do MongoDB. Um modelo `IsolationForest(contamination=0.2, random_state=42)` analisa o vetor `[req_por_minuto, taxa_4xx, rotas_distintas]`.
* **Resposta:** IPs com desvio estatístico extremo recebem `429 Too Many Requests` com cabeçalho `Retry-After: 60`. O script `test_traffic.py` automatiza o envio de tráfego legítimo versus rajada hostil para comprovar o bloqueio em tempo real.

### Exercício 10 — Desafio: Auditoria e Hardening Completo
* **Diretório:** `ex10_desafio_seguranca/`
* **Porta:** `5010`
* **Arquivos Entregues:**
  1. `app_vulneravel.py`: Aplicação original com múltiplas vulnerabilidades.
  2. `app_seguro.py`: Versão blindada (queries parametrizadas, escape XSS, autenticação, headers de segurança e tratamento de erros 500 sem stack trace).
  3. `exploit.py`: Prova de conceito demonstrando ataques contra as falhas mapeadas.
  4. `auditoria.md`: Relatório classificando 8 vulnerabilidades no OWASP Top 10 (2025), detalhando impacto, correções e explicitando as falhas por ausência (falta de logging e falta de headers defensivos).
* **Resultado dos Testes:** O mesmo `exploit.py` atinge **6/6 ataques bem-sucedidos** contra a versão vulnerável e **0/6** contra a versão segura.

---

## 🧪 Como Executar o Teste do Desafio (Ex 10)

Para testar o Exercício 10 com a ferramenta de exploit:

1. Em um terminal, inicie o app vulnerável:
   ```bash
   python ex10_desafio_seguranca/app_vulneravel.py
   ```
2. Em outro terminal, execute o exploit:
   ```bash
   python ex10_desafio_seguranca/exploit.py
   # Resultado esperado: 6 de 6 ataques bem-sucedidos
   ```
3. Encerre o app vulnerável (`Ctrl + C`), inicie o app seguro:
   ```bash
   python ex10_desafio_seguranca/app_seguro.py
   ```
4. Execute novamente o mesmo exploit:
   ```bash
   python ex10_desafio_seguranca/exploit.py
   # Resultado esperado: 0 de 6 ataques bem-sucedidos (todos defendidos)
   ```
