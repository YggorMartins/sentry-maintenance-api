# Sentry Maintenance API

> ⚠️ Projeto em desenvolvimento incremental. Este README será completado
> na etapa final, com descrição completa, endpoints, exemplos de uso e
> instruções de deploy.

API de gestão de manutenção aeronáutica para uma oficina certificada,
desenvolvida como projeto de portfólio.

## Status atual: Etapa 7 — Upload de Arquivos

- [x] Estrutura de pastas (Clean Architecture)
- [x] Configuração via `.env` (Pydantic Settings)
- [x] Docker + Docker Compose (API + PostgreSQL)
- [x] SQLAlchemy 2.0 + Alembic configurados
- [x] FastAPI básico com health check
- [x] Autenticação: registro, login, refresh (com rotação), logout (com revogação real via jti), `/auth/me`
- [x] Roles: admin, inspetor, mecanico, cliente + `RoleChecker` reutilizável
- [x] Clientes: PF/PJ unificados, validação de CPF/CNPJ (dígito verificador), endereço, paginação
- [x] Motores: TSN/TSO/TBO, número de série único
- [x] Aeronaves: prefixo/série únicos, motor 1:1, proprietário (cliente), filtro por proprietário
- [x] Ordens de Serviço: numeração automática (SEQUENCE), máquina de estados de status, mecânico/inspetor validados por papel
- [x] Inspeções: 50h/100h/anual/especial/progressiva, vinculadas a uma OS, responsável validado como Inspetor
- [x] Peças + Estoque: saldo controlado só por movimentações (livro-razão), bloqueio de saldo negativo
- [x] Anexos: upload polimórfico (aeronave/OS/cliente/inspeção), abstração de storage pronta para S3, validação de tipo/tamanho
- [x] Testes unitários: segurança (hash/JWT), CPF/CNPJ, schema de Motor, máquina de estados da OS, datas de Inspeção, quantidade de Movimentação, LocalStorageBackend
- [ ] Clientes (Etapa 2)
- [ ] Aeronaves + Motores (Etapa 3)
- [ ] Ordens de Serviço (Etapa 4)
- [ ] Inspeções (Etapa 5)
- [ ] Peças + Estoque (Etapa 6)
- [ ] Upload de arquivos (Etapa 7)
- [ ] Testes, segurança e documentação final (Etapa 8)

## Como rodar (ambiente de desenvolvimento)

```bash
cp .env.example .env
# ajuste as variáveis se necessário

docker compose up --build
```

A API sobe em `http://localhost:8000`. Verifique com:

```bash
curl http://localhost:8000/health
```

Documentação interativa (Swagger): `http://localhost:8000/docs`

Depois de subir os containers, aplique as migrations (dentro do container `api`):

```bash
docker compose exec api alembic upgrade head
```

Rode os testes:

```bash
docker compose exec api pytest -v
```

## Endpoints de autenticação (Etapa 1)

| Método | Rota            | Descrição                                    | Autenticado? |
|--------|-----------------|-----------------------------------------------|--------------|
| POST   | `/auth/register`| Cadastra novo usuário                          | Não          |
| POST   | `/auth/login`   | Autentica e retorna access + refresh token     | Não          |
| POST   | `/auth/refresh` | Gera novo par de tokens (rotaciona o refresh)  | Não          |
| POST   | `/auth/logout`  | Revoga o refresh token informado               | Não          |
| GET    | `/auth/me`      | Retorna os dados do usuário autenticado        | Sim          |

## Endpoints de clientes (Etapa 2)

| Método | Rota               | Descrição                          | Permissão                        |
|--------|--------------------|-------------------------------------|-----------------------------------|
| POST   | `/clientes`        | Cadastra cliente (PF ou PJ)         | admin, inspetor                   |
| GET    | `/clientes`        | Lista clientes (paginado)           | admin, inspetor, mecanico         |
| GET    | `/clientes/{id}`   | Consulta um cliente                 | admin, inspetor, mecanico         |
| PUT    | `/clientes/{id}`   | Atualiza um cliente                 | admin, inspetor                   |
| DELETE | `/clientes/{id}`   | Remove um cliente                   | admin, inspetor                   |

## Endpoints de motores (Etapa 3)

| Método | Rota              | Descrição                     | Permissão                          |
|--------|-------------------|---------------------------------|--------------------------------------|
| POST   | `/motores`        | Cadastra motor                  | admin, inspetor, mecanico            |
| GET    | `/motores`        | Lista motores (paginado)        | admin, inspetor, mecanico            |
| GET    | `/motores/{id}`   | Consulta um motor                | admin, inspetor, mecanico            |
| PUT    | `/motores/{id}`   | Atualiza um motor (TSN/TSO etc.) | admin, inspetor, mecanico            |
| DELETE | `/motores/{id}`   | Remove um motor                  | admin, inspetor, mecanico            |

## Endpoints de aeronaves (Etapa 3)

| Método | Rota                | Descrição                                     | Permissão                  |
|--------|---------------------|-------------------------------------------------|------------------------------|
| POST   | `/aeronaves`        | Cadastra aeronave (valida motor/proprietário)   | admin, inspetor              |
| GET    | `/aeronaves`        | Lista aeronaves (paginado, filtro por `cliente_id`) | admin, inspetor, mecanico |
| GET    | `/aeronaves/{id}`   | Consulta uma aeronave                            | admin, inspetor, mecanico    |
| PUT    | `/aeronaves/{id}`   | Atualiza uma aeronave                            | admin, inspetor              |
| DELETE | `/aeronaves/{id}`   | Remove uma aeronave                              | admin, inspetor              |

## Endpoints de ordens de serviço (Etapa 4)

| Método | Rota                          | Descrição                                          | Permissão                  |
|--------|-------------------------------|------------------------------------------------------|------------------------------|
| POST   | `/ordens-servico`             | Abre OS (número gerado automaticamente)               | admin, inspetor              |
| GET    | `/ordens-servico`              | Lista OS (filtros: `aeronave_id`, `status`, `mecanico_id`) | admin, inspetor, mecanico |
| GET    | `/ordens-servico/{id}`         | Consulta uma OS                                       | admin, inspetor, mecanico    |
| PUT    | `/ordens-servico/{id}`         | Edita campos (bloqueado se status terminal)            | admin, inspetor              |
| PATCH  | `/ordens-servico/{id}/status`  | Transição de status (valida máquina de estados)        | admin, inspetor              |
| DELETE | `/ordens-servico/{id}`         | Remove OS (só permitido em status `aberta`)            | admin                        |

## Endpoints de inspeções (Etapa 5)

| Método | Rota                    | Descrição                                                    | Permissão                  |
|--------|-------------------------|-----------------------------------------------------------------|------------------------------|
| POST   | `/inspecoes`            | Registra inspeção (valida OS e responsável = inspetor)          | admin, inspetor, mecanico    |
| GET    | `/inspecoes`            | Lista (filtros: `aeronave_id`, `ordem_servico_id`, `tipo`)       | admin, inspetor, mecanico    |
| GET    | `/inspecoes/{id}`       | Consulta uma inspeção                                            | admin, inspetor, mecanico    |
| PUT    | `/inspecoes/{id}`       | Atualiza uma inspeção                                            | admin, inspetor, mecanico    |
| DELETE | `/inspecoes/{id}`       | Remove uma inspeção                                              | admin                        |

## Endpoints de peças e estoque (Etapa 6)

| Método | Rota                          | Descrição                                                | Permissão                  |
|--------|-------------------------------|-------------------------------------------------------------|------------------------------|
| POST   | `/pecas`                      | Cadastra peça (`quantidade_atual` inicia em 0)               | admin, inspetor, mecanico    |
| GET    | `/pecas`                      | Lista peças (paginado)                                        | admin, inspetor, mecanico    |
| GET    | `/pecas/{id}`                 | Consulta uma peça                                              | admin, inspetor, mecanico    |
| PUT    | `/pecas/{id}`                 | Atualiza dados cadastrais (não altera quantidade)              | admin, inspetor, mecanico    |
| DELETE | `/pecas/{id}`                 | Remove peça (bloqueado se houver movimentações)                | admin                        |
| POST   | `/movimentacoes-estoque`      | Registra entrada/saída (ajusta saldo atomicamente)             | admin, inspetor, mecanico    |
| GET    | `/movimentacoes-estoque`      | Histórico (filtros: `peca_id`, `tipo`, `ordem_servico_id`)      | admin, inspetor, mecanico    |

## Endpoints de anexos (Etapa 7)

| Método | Rota                      | Descrição                                                     | Permissão                  |
|--------|---------------------------|-------------------------------------------------------------------|------------------------------|
| POST   | `/anexos`                 | Upload (multipart/form-data: `entidade_tipo`, `entidade_id`, `file`, `descricao`) | admin, inspetor, mecanico |
| GET    | `/anexos`                 | Lista (filtros: `entidade_tipo`, `entidade_id`)                    | admin, inspetor, mecanico    |
| GET    | `/anexos/{id}`            | Metadados de um anexo                                               | admin, inspetor, mecanico    |
| GET    | `/anexos/{id}/download`   | Baixa o arquivo                                                     | admin, inspetor, mecanico    |
| DELETE | `/anexos/{id}`            | Remove o anexo (banco + arquivo em disco)                           | admin, inspetor              |

Tipos de arquivo aceitos: PDF, JPG, PNG, DOC, DOCX. Tamanho máximo
configurável via `MAX_UPLOAD_SIZE_MB` no `.env` (padrão: 10MB).

`entidade_tipo` aceita: `aeronave`, `ordem_servico`, `cliente`,
`inspecao` — o `entidade_id` deve ser o UUID de um registro existente
daquele tipo (validado no upload).

Máquina de estados do `status`:

```
aberta ──────► em_andamento ──────► concluida
  │                 │  ▲
  │                 ▼  │
  │           aguardando_pecas
  │                 │
  └──────► cancelada ◄┘
```

## Stack

Python 3.12+, FastAPI, PostgreSQL, SQLAlchemy 2.0, Alembic, Pydantic V2,
Docker, JWT, Pytest.
