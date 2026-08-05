# Guia de Testes Manuais — Sentry Maintenance API

Este guia cobre: como subir o projeto, como acessar o Swagger, e o
passo a passo de cada teste manual sugerido nas Etapas 1 a 5.

---

## 1. Subindo o projeto

No terminal (PowerShell), dentro da pasta do projeto:

```bash
docker compose up --build -d
```

O `-d` roda em segundo plano ("detached"), liberando seu terminal. Se
quiser ver os logs em tempo real depois:

```bash
docker compose logs -f api
```

Aplique as migrations (cria as tabelas no banco):

```bash
docker compose exec api alembic upgrade head
```

Rode os testes automatizados:

```bash
docker compose exec api pytest -v
```

Para parar tudo:

```bash
docker compose down
```

Para parar E apagar os dados do banco (recomeçar do zero):

```bash
docker compose down -v
```

---

## 2. Acessando o Swagger (documentação interativa)

Com os containers rodando, abra o navegador em:

```
http://localhost:8000/docs
```

Não precisa "baixar" nada — o Swagger é gerado automaticamente pelo
FastAPI e servido pela própria API. Você vai ver todos os endpoints
organizados por módulo (Autenticação, Clientes, Motores, Aeronaves,
Ordens de Serviço, Inspeções), cada um com um botão **"Try it out"**.

### Como autenticar no Swagger

1. Primeiro registre um usuário admin (endpoint `POST /auth/register`,
   veja o passo a passo abaixo).
2. Faça login em `POST /auth/login` e copie o valor de `access_token`
   da resposta.
3. Clique no botão **"Authorize"** (cadeado, no topo direito da
   página).
4. Cole **só o token** (sem a palavra "Bearer", o Swagger já adiciona)
   e clique em "Authorize", depois "Close".
5. A partir daí, todo "Try it out" já envia o token automaticamente.

O access token expira em 30 minutos — se começar a receber `401`, é
só logar de novo (ou usar `/auth/refresh`).

---

## 3. Etapa 1 — Autenticação

**Objetivo:** validar login, JWT, e que logout realmente revoga o
refresh token (não é só cosmético no cliente).

1. `POST /auth/register` — crie um usuário com `role: "admin"`.
2. `POST /auth/login` — copie `access_token` e `refresh_token` da
   resposta.
3. Clique em **Authorize** e cole o `access_token`.
4. `GET /auth/me` — deve retornar os dados do usuário logado.
5. `POST /auth/refresh` — envie o `refresh_token` no corpo. Deve
   devolver um par novo de tokens.
6. `POST /auth/logout` — envie o **mesmo** `refresh_token` usado no
   passo 5 (ele já foi rotacionado, então este teste é sobre o token
   novo retornado no passo 5).
7. Tente `POST /auth/refresh` de novo com esse token recém-revogado —
   **deve retornar 401**. Isso prova que o logout realmente invalidou
   o token no banco, não é só "esquecer" ele no cliente.

---

## 4. Etapa 2 — Clientes

**Objetivo:** validar a regra de CPF/CNPJ (dígito verificador) e a
checagem de duplicidade.

1. `POST /clientes` com:
   ```json
   {
     "tipo_pessoa": "fisica",
     "nome": "Fulano de Tal",
     "cpf": "111.444.777-35",
     "email": "fulano@exemplo.com"
   }
   ```
   CPF válido — deve retornar `201`.
2. Repita o mesmo `POST` com o mesmo CPF — deve retornar `409`
   (duplicidade).
3. Tente criar outro cliente com `"cpf": "111.111.111-11"` — deve
   retornar `422` **antes** de tentar salvar (dígito verificador
   inválido, um CPF com todos os dígitos iguais nunca é válido).
4. Tente `"tipo_pessoa": "fisica"` informando `cnpj` em vez de `cpf` —
   deve retornar `422` (documento incompatível com o tipo de pessoa).

---

## 5. Etapa 3 — Motores e Aeronaves

**Objetivo:** validar que um motor não pode estar em duas aeronaves
ao mesmo tempo.

1. `POST /motores`:
   ```json
   {
     "fabricante": "Lycoming",
     "modelo": "O-360",
     "numero_serie": "L-12345-51A",
     "tsn": 500,
     "tso": 100,
     "tbo": 2000
   }
   ```
   Guarde o `id` retornado.
2. `POST /aeronaves`, usando o `id` do cliente criado na Etapa 2 e do
   motor criado acima:
   ```json
   {
     "prefixo": "PT-ABC",
     "fabricante": "Cessna",
     "modelo": "172",
     "numero_serie": "17280123",
     "ano": 2015,
     "categoria": "monomotor",
     "cliente_id": "<id do cliente>",
     "motor_id": "<id do motor>"
   }
   ```
   Deve retornar `201`.
3. Tente criar uma **segunda** aeronave com o **mesmo** `motor_id` —
   deve retornar `409` (motor já instalado em outra aeronave).

---

## 6. Etapa 4 — Ordens de Serviço

**Objetivo:** validar a máquina de estados do `status`.

1. `POST /ordens-servico`, usando o `id` da aeronave criada acima:
   ```json
   {
     "aeronave_id": "<id da aeronave>",
     "descricao": "Revisão de 100 horas"
   }
   ```
   Guarde o `id` e note o `numero` gerado automaticamente
   (`OS-000001`).
2. `PATCH /ordens-servico/{id}/status` com `{"status": "concluida"}` —
   **deve retornar 409**. Você não pode pular direto de `aberta` para
   `concluida`.
3. `PATCH /ordens-servico/{id}/status` com
   `{"status": "em_andamento"}` — deve funcionar (`200`).
4. `PATCH /ordens-servico/{id}/status` com `{"status": "concluida"}` —
   agora deve funcionar, e o campo `data_fechamento` na resposta deve
   vir preenchido automaticamente (você nunca envia essa data, o
   sistema preenche sozinho).
5. Tente `PUT /ordens-servico/{id}` (editar descrição, por exemplo)
   nessa OS já concluída — deve retornar `409` (estado terminal não é
   editável).

---

## 7. Etapa 5 — Inspeções

**Objetivo:** validar que o responsável precisa ter o papel de
Inspetor, não qualquer usuário.

1. Registre um segundo usuário com `role: "mecanico"` (`POST
   /auth/register`) e anote o `id` dele (pode consultar via `GET
   /auth/me` logando com ele, ou você mesmo anota no cadastro).
2. `POST /inspecoes`, usando o `id` da OS criada na Etapa 4 e o `id`
   do usuário **mecânico**:
   ```json
   {
     "ordem_servico_id": "<id da OS>",
     "responsavel_id": "<id do usuário mecânico>",
     "tipo": "anual",
     "data": "2026-08-01",
     "horas_aeronave": 1200,
     "itens_executados": "Inspeção geral da célula e motor."
   }
   ```
   **Deve retornar 400** — o responsável precisa ser um `inspetor`,
   não um `mecanico`.
3. Registre (ou use) um usuário com `role: "inspetor"` e repita o
   `POST` com o `id` dele em `responsavel_id` — agora deve retornar
   `201`.

---

## Dica geral

Sempre que um teste "deveria dar erro", confira dois números: o
**status HTTP** (401, 404, 409, 422...) e a mensagem em `detail` na
resposta — ela deve ser específica sobre o que deu errado, não um
erro genérico. Isso é o reflexo direto das exceções de domínio que
fomos criando em `app/core/exceptions.py` ao longo das etapas.
