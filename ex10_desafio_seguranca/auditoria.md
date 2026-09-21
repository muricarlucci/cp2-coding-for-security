# Auditoria de segurança — Exercício 10

| Falha | OWASP 2025 | Impacto | Mitigação aplicada |
|---|---|---|---|
| SQL Injection em busca | A05 Injection | Leitura indevida de usuários | Placeholder `%s` para o termo LIKE. |
| XSS refletido no perfil | A05 Injection | Execução de script no navegador | `html.escape` antes de compor HTML. |
| DELETE sem autenticação | A01 Broken Access Control | Remoção arbitrária de contas | Chave de API e verificação de privilégio. |
| Debug/erro detalhado | A02 Security Misconfiguration | Vazamento de schema e traceback | `debug=False` e handler 500 genérico. |
| Exposição da coluna senha | A01 Broken Access Control | Divulgação de dado sensível a quem não tem autorização para recebê-lo | Seleção explícita sem a coluna sensível. |
| Headers de segurança ausentes | A02 Security Misconfiguration | Maior superfície para XSS, MIME sniffing e clickjacking | CSP, `nosniff` e `DENY` em todas as respostas. |
| Ausência de logging | A09 Security Logging and Alerting Failures | Ataques não deixam evidência investigável | Registro estruturado de cada requisição e erro. |
| Falta de tratamento de exceções | A10 Mishandling of Exceptional Conditions | Falhas internas expõem detalhes e tornam a API instável | Handler único, resposta genérica e log interno. |
| Credencial no código original | A02 Security Misconfiguration | Segredo pode vazar em repositórios | Configuração exclusivamente por `.env`/variáveis de ambiente. |
