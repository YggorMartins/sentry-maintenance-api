# Política de segurança

## Versões suportadas

A versão mais recente da branch `main` recebe correções de segurança.

## Como relatar uma vulnerabilidade

Não abra uma issue pública com credenciais, dados pessoais ou detalhes
exploráveis. Envie um relato privado pelo recurso **Security Advisories** do
repositório, incluindo impacto, passos mínimos para reprodução e a versão
afetada. Evite acessar ou alterar dados que não pertençam à sua conta.

## Operação segura

- Nunca versione `.env`, chaves JWT, senhas ou arquivos enviados por usuários.
- Em produção, use `APP_ENV=production`; a validação bloqueia segredo fraco,
  debug ativo, hosts/CORS genéricos, banco com senha trivial e rate limiting
  sem Redis.
- Crie o primeiro administrador com `python -m app.cli.create_admin`. O
  endpoint público de registro nunca concede papel privilegiado.
- Execute `pip-audit -r requirements.txt` e a suíte de testes antes do deploy.
- Termine TLS em um proxy confiável e mantenha PostgreSQL e Redis em rede
  privada.
