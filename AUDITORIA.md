# Auditoria técnica — Sentry Maintenance API

Data: 16/09/2026

## Resumo executivo

O repositório original já possuía uma boa base: FastAPI com separação em routers/services/repositories, autenticação JWT com rotação de refresh token, Argon2id, RBAC, validação de upload por assinatura, proteção contra path traversal, rate limiting e configuração de produção validada.

Não foram encontradas credenciais reais versionadas. Os valores presentes em `.env.example`, testes e Docker Compose são exemplos explícitos e a aplicação bloqueia valores fracos em produção.

As principais lacunas estavam no domínio necessário ao painel, na ausência de leituras agregadas e nos índices para essas leituras. Elas foram corrigidas sem quebrar os contratos anteriores.

## Achados e correções

### Segurança e qualidade

- **Configuração e segredos:** mantida a leitura exclusiva por `pydantic-settings`; `.env` permanece ignorado. A validação já exige chave JWT, senha de banco, CORS e hosts seguros em produção.
- **Autorização:** os novos endpoints usam o RBAC existente. Agenda pode ser consultada por equipe técnica e alterada apenas por admin/inspetor; dashboard é restrito à equipe.
- **Validação:** contratos de agenda rejeitam campos extras, intervalos invertidos e recorrência anterior à data inicial. Custos, estoque mínimo e limites de texto possuem restrições tipadas.
- **Exceções:** o handler global existente continua ocultando detalhes internos; os novos erros de domínio são traduzidos para respostas 404/422 controladas.
- **Supply chain:** `pip-audit` não encontrou vulnerabilidades conhecidas nas dependências Python; `npm audit` reportou zero vulnerabilidades.

### Escalabilidade e performance

- Criado `DashboardRepository`, concentrando agregações SQL no banco em vez de montar KPIs em memória.
- A listagem principal usa joins explícitos de O.S., aeronave e técnico, eliminando N+1.
- Categorias, custos, alertas e disponibilidade usam `COUNT`, `SUM`, `GROUP BY` e subqueries.
- O endpoint consolidado `/dashboard/resumo` reduz múltiplas viagens HTTP a uma chamada.
- Adicionados índices compostos para status/data da O.S., prazo, alerta de estoque e intervalo/relacionamentos da agenda.
- Paginação e limite máximo de período (366 dias) protegem consultas amplas.

### Domínio e arquitetura

- O.S. agora registra tipo, categoria, custo estimado e prazo, preservando valores padrão para compatibilidade.
- Peças agora registram categoria e estoque mínimo.
- Nova entidade `AgendamentoManutencao` com recorrência, status, técnico e intervalo.
- Regras continuam separadas em schemas, models, repositories, services e routers.
- Migração Alembic reversível adicionada em `b913d8ae12f4_add_dashboard_and_scheduling.py`.

## Novos endpoints

| Método | Rota | Finalidade |
|---|---|---|
| GET | `/dashboard/resumo` | KPIs, O.S. ativas, categorias e composição de custos |
| GET | `/dashboard/tecnicos/disponibilidade` | Carga ativa e próxima atividade dos técnicos |
| GET | `/agendamentos` | Agenda paginada e filtrável por intervalo |
| POST | `/agendamentos` | Novo agendamento, inclusive recorrente |
| PUT | `/agendamentos/{id}` | Atualização e mudança de status |
| DELETE | `/agendamentos/{id}` | Exclusão administrativa |

Os endpoints existentes de `/ordens-servico` e `/pecas` foram expandidos com os novos campos.

## Frontend

O projeto React/TypeScript/Tailwind está em `/frontend`, com:

- shell responsivo (header, sidebar e rotas);
- cards de KPI, tabela de O.S., distribuição por categoria e composição de custos;
- estados de carregamento e erro;
- integração Axios com Bearer token e endpoint agregado;
- mock visual ativado por padrão para abrir o dashboard sem banco populado;
- configuração `VITE_USE_MOCKS=false` para consumir a API real.

## Verificação

- Backend: **72 testes aprovados**.
- Frontend: TypeScript e build Vite aprovados.
- Dependências: zero vulnerabilidades conhecidas em `pip-audit` e `npm audit`.
- Layout: verificado em breakpoints móvel e desktop no navegador.
- Desktop: build Windows validado com PyInstaller; executável gerado em modo `onedir`.

## Empacotamento desktop

- `main_desktop.py` configura um banco SQLite e diretórios persistentes em
  `%LOCALAPPDATA%\SentryMaintenance`, cria as tabelas na primeira execução,
  inicia o FastAPI em uma porta local livre e aguarda o health check antes de
  abrir a janela nativa.
- `app/core/spa.py` serve as rotas do React Router sem mascarar assets ausentes.
- `build_windows.bat` compila o React, substitui `app/static` e executa o
  PyInstaller com os recursos estáticos incluídos.
- `SentryMaintenance.spec` e `requirements-desktop.txt` tornam o build
  reproduzível fora do ambiente de desenvolvimento.

Risco residual: o rate limiter em memória é adequado apenas para desenvolvimento; produção já exige Redis. Recomenda-se também telemetria (OpenTelemetry/Sentry), backup testado do PostgreSQL e testes E2E autenticados antes do go-live.
