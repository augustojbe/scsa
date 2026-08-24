# Arquitetura

## Multi-tenant compartilhado

O SCSI usa arquitetura multi-tenant **compartilhada** (mesmo banco, mesmo schema).
O isolamento é feito pelo campo-chave `brokerage` (FK para `core.Brokerage`) nos
models sensíveis, com filtros obrigatórios via `TenantManager`, middleware de
tenant e validação em forms/admin.

```mermaid
flowchart TB
  subgraph Shared[PostgreSQL — Schema Único]
    B[Brokerage A] & B2[Brokerage B]
    C1[Client A] --> B
    C2[Client B] --> B2
    P1[Policy A] --> B
    P2[Policy B] --> B2
  end
  ReqA[Request User A] -->|filtra brokerage=A| C1
  ReqB[Request User B] -->|filtra brokerage=B| C2
  ReqA -.never.-> C2
  ReqB -.never.-> C1
```

## Apps Django

| App | Responsabilidade |
|---|---|
| `core` | settings, urls, custom user, Brokerage, middleware, healthcheck |
| `base` | models base, tenant manager, mixins, context processors, notificações |
| `accounts` | onboarding de corretora, login |
| `clients` | clientes + anexos |
| `insurers` | seguradoras e ramos |
| `policies` | propostas, apólices, coberturas, itens, endossos, anexos |
| `claims` | sinistros + anexos |
| `crm` | pipelines, etapas, negociações (grid/kanban) |
| `renewals` | renovações |
| `agents` | agentes e produtores |
| `commissions` | comissões e repasses |
| `reports` | relatórios PDF/CSV |
| `dashboard` | dashboard e métricas |
| `ai` | resumos, chat, tasks Celery |

## Tarefas assíncronas

```mermaid
flowchart LR
  App[App Django] -->|dispara task| CeleryW[Celery Worker]
  CeleryW --> RabbitMQ[(RabbitMQ)]
  CeleryW --> Redis[(Redis)]
  CeleryW --> DB[(PostgreSQL)]
```

Processamentos pesados (resumos de IA) rodam via Celery para não bloquear a
interface. Ao concluir, criam uma notificação interna.

## Redes Docker (produção)

```mermaid
flowchart LR
  subgraph TP[traefik_public - external]
    T[Traefik]
    APP[app]
  end
  subgraph IN[scsi_v1_internal - internal]
    APP
    DB[(db)]
    RD[(redis)]
    RB[(rabbitmq)]
    CW[celery_worker]
    CB[celery_beat]
  end
  subgraph EG[scsi_v1_egress]
    CW
    CB
  end
  T --> APP
```
