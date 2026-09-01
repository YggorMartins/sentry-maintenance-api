# Sentry Maintenance API

API REST para gestão de manutenção aeronáutica de uma oficina
certificada — controle de clientes, aeronaves, motores, ordens de
serviço, inspeções, estoque de peças e anexos digitais. Projeto de
portfólio construído em etapas incrementais, com arquitetura em
camadas, testes automatizados e Docker.

## Descrição

O sistema simula o dia a dia de uma oficina de manutenção aeronáutica
certificada: cadastro de clientes (pessoa física/jurídica), aeronaves
e seus motores, abertura e acompanhamento de Ordens de Serviço com
máquina de estados, registro de inspeções regulatórias (50h, 100h,
anual, especial, progressiva), controle de estoque de peças por
movimentação (entrada/saída, nunca edição direta de saldo), e upload
de documentos (certificados, laudos, OS digitalizadas). Autenticação
via JWT com controle de acesso por papel (admin, inspetor, mecânico,
cliente).

## Tecnologias

- **Python 3.12+** / **FastAPI** — framework web assíncrono, com
  documentação OpenAPI/Swagger automática
- **PostgreSQL** + **SQLAlchemy 2.0** (ORM, estilo `Mapped`/`mapped_column`)
- **Alembic** — migrations versionadas
- **Pydantic V2** — validação de entrada/saída
- **JWT** (`PyJWT`) + **Argon2id** (`pwdlib`) — autenticação e hash de senha
- **Redis** — limite de tentativas compartilhado entre réplicas
- **Docker** + **Docker Compose** — API, banco e Redis containerizados
- **Pytest** — testes unitários (funções puras) e de integração (HTTP + banco real)

## Arquitetura

Camadas separadas por responsabilidade técnica (não por feature),
seguindo os princípios de Clean Architecture adaptados a um projeto
FastAPI:

```
Requisição HTTP
      │
      ▼
  routers/        → só HTTP: recebe request, valida com schema, chama service, traduz exceção → status HTTP
      │
      ▼
  services/        → regra de negócio pura (não sabe o que é HTTP nem SQL)
      │
      ▼
  repositories/     → única camada que fala com o banco (queries SQLAlchemy)
      │
      ▼
  models/           → entidades ORM (SQLAlchemy)
```

Complementando:
- **`schemas/`** — contratos Pydantic de entrada/saída da API (nunca os mesmos objetos que os `models/`)
- **`core/`** — transversais: segurança (hash/JWT), exceções de domínio, enums, storage, logging
- **`dependencies/`** — dependências injetáveis do FastAPI (usuário autenticado, checagem de papel)
- **`config/`** — leitura centralizada de variáveis de ambiente

Essa separação permite, por exemplo, testar regra de negócio sem
banco real (mockando o repository), ou trocar PostgreSQL por outro
banco sem tocar em `services/`.

### Decisões de design que valem a pena destacar

- **Dados derivados nunca são duplicados**: o cliente de uma Ordem de
  Serviço não é armazenado na própria OS — é obtido via
  `ordem.aeronave.cliente`. Evita duas fontes de verdade.
- **Estoque é um livro-razão**: `Peca.quantidade_atual` só muda
  através de registros de `MovimentacaoEstoque` (entrada/saída),
  nunca editado diretamente — dá rastreabilidade completa de graça.
- **Máquina de estados para Ordem de Serviço**: transições de
  `status` são validadas contra uma tabela de transições permitidas,
  não um campo livre.
- **Numeração de OS atômica**: usa uma `SEQUENCE` nativa do
  PostgreSQL, evitando race conditions sob requisições concorrentes.
- **Abstração de armazenamento (Strategy Pattern)**: upload de
  arquivos passa por uma interface `StorageBackend`; hoje só existe
  `LocalStorageBackend` (disco), mas trocar para AWS S3 no futuro
  exige só uma nova implementação da interface, sem tocar no resto do
  sistema.
- **Revogação real de sessão**: logout marca o `jti` do refresh token
  como revogado no banco — não é só o cliente "esquecer" o token.
- **Privilégio mínimo**: o cadastro público sempre cria um cliente;
  contas administrativas são criadas somente pelo comando de bootstrap.
- **Defesa contra abuso**: login, cadastro e renovação de token possuem
  limites de tentativas, com Redis quando há múltiplas instâncias.
- **Upload verificado**: tamanho, extensão e assinatura real do arquivo
  são validados, e caminhos fora do diretório de uploads são recusados.

## Estrutura de pastas

```
sentry-maintenance-api/
├── app/
│   ├── main.py                 # ponto de entrada, middlewares, exception handler
│   ├── api/
│   ├── auth/
│   ├── config/
│   │   └── settings.py         # configuração centralizada (Pydantic Settings)
│   ├── core/
│   │   ├── security.py         # hash de senha, JWT
│   │   ├── exceptions.py       # exceções de domínio
│   │   ├── enums.py            # enums compartilhados (roles, status, tipos)
│   │   ├── storage.py          # abstração de armazenamento de arquivos
│   │   └── logging.py          # configuração de logging
│   ├── database/
│   │   └── session.py          # engine, sessão, Base declarativa
│   ├── models/                 # entidades SQLAlchemy
│   ├── schemas/                # contratos Pydantic
│   ├── repositories/           # acesso a dados (única camada que fala com o banco)
│   ├── services/                # regra de negócio
│   ├── dependencies/            # dependências injetáveis (auth, RoleChecker)
│   ├── routers/                 # endpoints REST
│   ├── utils/                   # funções puras reutilizáveis (validador de CPF/CNPJ)
│   └── tests/
│       ├── conftest.py         # fixtures de teste (sessão isolada + client HTTP)
│       ├── helpers.py          # funções auxiliares dos testes de integração
│       ├── test_*_schema.py    # testes unitários (funções puras, sem banco)
│       └── test_*_flow.py      # testes de integração (HTTP real + banco real)
├── alembic/
│   └── versions/                # migrations versionadas
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── requirements-dev.txt
└── .env.example
```

## Como instalar

Pré-requisitos: Docker e Docker Compose instalados.

```bash
git clone <url-do-repositorio>
cd sentry-maintenance-api
cp .env.example .env
```

Ajuste no `.env` a senha do PostgreSQL e a `SECRET_KEY`. A senha usada
em `POSTGRES_PASSWORD` deve ser a mesma presente em `DATABASE_URL`.

## Como executar

```bash
docker compose up --build -d
docker compose exec api alembic upgrade head
docker compose exec api python -m app.cli.create_admin \
  --email admin@oficina.com --full-name "Administrador"
```

A API sobe em `http://localhost:8000`.

- Documentação interativa (Swagger): `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

Para parar:

```bash
docker compose down
```

Para parar e apagar os dados do banco:

```bash
docker compose down -v
```

## Variáveis de ambiente

| Variável                      | Descrição                                             | Padrão                     |
|--------------------------------|--------------------------------------------------------|------------------------------|
| `APP_NAME`                    | Nome da aplicação                                       | `Sentry Maintenance API`     |
| `APP_ENV`                     | Ambiente (`development`/`production`)                   | `development`                |
| `DEBUG`                       | Ativa echo de SQL e nível de log DEBUG                   | `True`                        |
| `DATABASE_URL`                | String de conexão PostgreSQL                             | —                              |
| `SECRET_KEY`                  | Chave de assinatura dos JWT (troque em produção!)         | —                              |
| `ALGORITHM`                   | Algoritmo do JWT                                          | `HS256`                        |
| `JWT_ISSUER`                  | Emissor esperado nos tokens                               | `sentry-maintenance-api`       |
| `JWT_AUDIENCE`                | Audiência esperada nos tokens                             | `sentry-maintenance-clients`   |
| `ACCESS_TOKEN_EXPIRE_MINUTES`  | Validade do access token                                  | `30`                            |
| `REFRESH_TOKEN_EXPIRE_DAYS`   | Validade do refresh token                                 | `7`                              |
| `CORS_ORIGINS`                | Origens permitidas, separadas por vírgula                  | `*` apenas em desenvolvimento   |
| `ALLOWED_HOSTS`               | Hosts HTTP permitidos, separados por vírgula               | `*` apenas em desenvolvimento   |
| `RATE_LIMIT_REDIS_URL`        | Redis compartilhado para limitação de tentativas           | —                               |
| `UPLOAD_DIR`                  | Diretório de armazenamento local de anexos                 | `app/uploads`                    |
| `MAX_UPLOAD_SIZE_MB`          | Tamanho máximo de upload                                    | `10`                              |

## Endpoints

### Autenticação

| Método | Rota            | Descrição                                    | Autenticado? |
|--------|-----------------|-------------------------------------------------|--------------|
| POST   | `/auth/register`| Cadastra novo usuário sempre como `cliente`       | Não          |
| POST   | `/auth/login`   | Autentica e retorna access + refresh token       | Não          |
| POST   | `/auth/refresh` | Gera novo par de tokens (rotaciona o refresh)    | Não          |
| POST   | `/auth/logout`  | Revoga o refresh token informado                 | Não          |
| GET    | `/auth/me`      | Retorna os dados do usuário autenticado          | Sim          |

### Clientes

| Método | Rota               | Descrição                | Permissão                  |
|--------|--------------------|----------------------------|------------------------------|
| POST   | `/clientes`        | Cadastra cliente (PF/PJ)    | admin, inspetor              |
| GET    | `/clientes`        | Lista (paginado)             | admin, inspetor, mecanico    |
| GET    | `/clientes/{id}`   | Consulta                      | admin, inspetor, mecanico    |
| PUT    | `/clientes/{id}`   | Atualiza                      | admin, inspetor              |
| DELETE | `/clientes/{id}`   | Remove                        | admin, inspetor              |

### Motores

| Método | Rota              | Descrição            | Permissão                  |
|--------|-------------------|------------------------|------------------------------|
| POST   | `/motores`        | Cadastra                | admin, inspetor, mecanico    |
| GET    | `/motores`        | Lista (paginado)         | admin, inspetor, mecanico    |
| GET    | `/motores/{id}`   | Consulta                  | admin, inspetor, mecanico    |
| PUT    | `/motores/{id}`   | Atualiza (TSN/TSO etc.)   | admin, inspetor, mecanico    |
| DELETE | `/motores/{id}`   | Remove                     | admin, inspetor, mecanico    |

### Aeronaves

| Método | Rota                | Descrição                                     | Permissão                  |
|--------|---------------------|---------------------------------------------------|------------------------------|
| POST   | `/aeronaves`        | Cadastra (valida motor/proprietário)                | admin, inspetor              |
| GET    | `/aeronaves`        | Lista (paginado, filtro `cliente_id`)                | admin, inspetor, mecanico    |
| GET    | `/aeronaves/{id}`   | Consulta                                              | admin, inspetor, mecanico    |
| PUT    | `/aeronaves/{id}`   | Atualiza                                              | admin, inspetor              |
| DELETE | `/aeronaves/{id}`   | Remove                                                | admin, inspetor              |

### Ordens de Serviço

| Método | Rota                          | Descrição                                          | Permissão                  |
|--------|-------------------------------|--------------------------------------------------------|------------------------------|
| POST   | `/ordens-servico`             | Abre OS (número gerado automaticamente)                 | admin, inspetor              |
| GET    | `/ordens-servico`              | Lista (filtros: `aeronave_id`, `status`, `mecanico_id`)  | admin, inspetor, mecanico    |
| GET    | `/ordens-servico/{id}`         | Consulta                                                  | admin, inspetor, mecanico    |
| PUT    | `/ordens-servico/{id}`         | Edita campos (bloqueado se status terminal)               | admin, inspetor              |
| PATCH  | `/ordens-servico/{id}/status`  | Transição de status (máquina de estados)                  | admin, inspetor              |
| DELETE | `/ordens-servico/{id}`         | Remove (só permitido em status `aberta`)                   | admin                        |

Máquina de estados:

```
aberta ──────► em_andamento ──────► concluida
  │                 │  ▲
  │                 ▼  │
  │           aguardando_pecas
  │                 │
  └──────► cancelada ◄┘
```

### Inspeções

| Método | Rota                    | Descrição                                                    | Permissão                  |
|--------|-------------------------|-------------------------------------------------------------------|------------------------------|
| POST   | `/inspecoes`            | Registra (valida OS e responsável = inspetor)                      | admin, inspetor, mecanico    |
| GET    | `/inspecoes`            | Lista (filtros: `aeronave_id`, `ordem_servico_id`, `tipo`)           | admin, inspetor, mecanico    |
| GET    | `/inspecoes/{id}`       | Consulta                                                             | admin, inspetor, mecanico    |
| PUT    | `/inspecoes/{id}`       | Atualiza                                                              | admin, inspetor, mecanico    |
| DELETE | `/inspecoes/{id}`       | Remove                                                                | admin                        |

### Peças e Estoque

| Método | Rota                          | Descrição                                                | Permissão                  |
|--------|-------------------------------|-------------------------------------------------------------|------------------------------|
| POST   | `/pecas`                      | Cadastra (`quantidade_atual` inicia em 0)                     | admin, inspetor, mecanico    |
| GET    | `/pecas`                      | Lista (paginado)                                               | admin, inspetor, mecanico    |
| GET    | `/pecas/{id}`                 | Consulta                                                        | admin, inspetor, mecanico    |
| PUT    | `/pecas/{id}`                 | Atualiza cadastro (não altera quantidade)                       | admin, inspetor, mecanico    |
| DELETE | `/pecas/{id}`                 | Remove (bloqueado se houver movimentações)                      | admin                        |
| POST   | `/movimentacoes-estoque`      | Registra entrada/saída (ajusta saldo atomicamente)               | admin, inspetor, mecanico    |
| GET    | `/movimentacoes-estoque`      | Histórico (filtros: `peca_id`, `tipo`, `ordem_servico_id`)         | admin, inspetor, mecanico    |

### Anexos

| Método | Rota                      | Descrição                                                     | Permissão                  |
|--------|---------------------------|---------------------------------------------------------------------|------------------------------|
| POST   | `/anexos`                 | Upload (multipart: `entidade_tipo`, `entidade_id`, `file`, `descricao`)| admin, inspetor, mecanico |
| GET    | `/anexos`                 | Lista (filtros: `entidade_tipo`, `entidade_id`)                       | admin, inspetor, mecanico    |
| GET    | `/anexos/{id}`            | Metadados                                                              | admin, inspetor, mecanico    |
| GET    | `/anexos/{id}/download`   | Baixa o arquivo                                                        | admin, inspetor, mecanico    |
| DELETE | `/anexos/{id}`            | Remove (banco + arquivo em disco)                                       | admin, inspetor              |

Tipos aceitos: PDF, JPG, PNG, DOC, DOCX. `entidade_tipo` aceita:
`aeronave`, `ordem_servico`, `cliente`, `inspecao`.

## Exemplos de requisições

**Registro de cliente + login:**

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"full_name": "Cliente", "email": "cliente@oficina.com", "password": "SenhaForte123"}'

curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "cliente@oficina.com", "password": "SenhaForte123"}'
# → { "access_token": "...", "refresh_token": "...", "token_type": "bearer" }
```

**Criar cliente (autenticado):**

```bash
curl -X POST http://localhost:8000/clientes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"tipo_pessoa": "fisica", "nome": "Fulano de Tal", "cpf": "111.444.777-35"}'
```

**Abrir uma Ordem de Serviço e mudar o status:**

```bash
curl -X POST http://localhost:8000/ordens-servico \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"aeronave_id": "<uuid-da-aeronave>", "descricao": "Revisão de 100 horas"}'

curl -X PATCH http://localhost:8000/ordens-servico/<id>/status \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"status": "em_andamento"}'
```

**Upload de anexo (multipart):**

```bash
curl -X POST http://localhost:8000/anexos \
  -H "Authorization: Bearer <access_token>" \
  -F "entidade_tipo=aeronave" \
  -F "entidade_id=<uuid-da-aeronave>" \
  -F "descricao=Certificado de aeronavegabilidade" \
  -F "file=@certificado.pdf"
```

## Como executar os testes

```bash
python -m pip install -r requirements-dev.txt
pytest -v
pip-audit -r requirements.txt
```

O projeto tem dois tipos de teste:

- **Unitários** (`test_*_schema.py`, `test_security.py`,
  `test_document_validators.py`, `test_storage.py`,
  `test_ordem_servico_status.py`): testam funções e validações puras
  — não tocam o banco, rodam em milissegundos.
- **De integração** (`test_*_flow.py`): sobem a aplicação FastAPI
  completa e testam o fluxo real via HTTP (registro → login →
  criação de recursos → regras de negócio). Por padrão usam SQLite
  em memória, portanto também rodam sem Docker. Para uma segunda
  validação contra PostgreSQL, defina `TEST_DATABASE_URL` com a URL
  de um banco dedicado; ele será criado automaticamente caso ainda
  não exista. Cobrem Autenticação, Clientes, Aeronaves e Ordens de
  Serviço.

Para rodar só uma categoria:

```bash
pytest app/tests/test_auth_flow.py -v
pytest -k "schema" -v
```

As dependências de teste ficam separadas da imagem de produção para
reduzir superfície de ataque e tamanho do contêiner.

## Deploy

Este projeto está pronto para rodar em qualquer ambiente com Docker.
Para um deploy real (fora do ambiente de desenvolvimento local), os
pontos de atenção são:

1. **Variáveis de ambiente**: gere uma `SECRET_KEY` forte
   (`openssl rand -hex 32`), defina `DEBUG=False`, `APP_ENV=production`,
   `ALLOWED_HOSTS` e origens CORS explícitas. A aplicação se recusa a
   iniciar em produção com valores inseguros.
2. **Banco de dados**: em produção, prefira um PostgreSQL gerenciado
   (RDS, Cloud SQL, etc.) em vez do container do `docker-compose.yml`
   (que é pensado para desenvolvimento local) — aponte `DATABASE_URL`
   para ele.
3. **Migrations**: rode `alembic upgrade head` como parte do processo
   de deploy (antes de trocar o tráfego pra nova versão), nunca
   manualmente em produção.
4. **Uploads**: o `LocalStorageBackend` grava em disco local, o que
   não sobrevive a redeploys/múltiplas instâncias em ambientes cloud
   — nesse cenário, implemente `S3StorageBackend` (mesma interface
   `StorageBackend` em `app/core/storage.py`) e troque a instância
   retornada por `get_storage_backend()`.
5. **HTTPS/reverse proxy**: o Uvicorn dentro do container não deve
   ficar exposto diretamente à internet — coloque atrás de um reverse
   proxy (nginx, Caddy, ou o load balancer do seu provedor cloud) que
   termine TLS.
6. **CORS**: restrinja `CORS_ORIGINS` ao domínio real do frontend em
   produção (nunca deixe `*` fora de desenvolvimento).
7. **Escala horizontal**: use um Redis compartilhado em
   `RATE_LIMIT_REDIS_URL`; não dependa do contador em memória.
