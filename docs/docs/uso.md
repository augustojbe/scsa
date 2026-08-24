# Uso

## Login

O login é feito por **e-mail** (usuário customizado do Django). Recuperação de
senha por e-mail usa o fluxo nativo.

## Módulos

### Dashboard
Métricas da carteira (clientes, apólices, prêmios, comissões), gráficos
(apólices por ramo/seguradora, clientes por tipo) e funil de negociações.

### Clientes / Seguradoras / Ramos
Cadastros base com CRUD, busca e anexos privados.

### Propostas e Apólices
- Criar proposta (cliente, seguradora, ramo, coberturas, itens cobertos, prêmio).
- Botão **Gerar apólice** cria a apólice a partir da proposta e marca a proposta
  como convertida.

### Sinistros
Vinculados a uma apólice + item coberto, com anexos e reserva.

### CRM
- **Grid:** tabela de negociações com filtros.
- **Kanban:** colunas = etapas do pipeline, com drag-and-drop para mover a etapa.
- Pipelines e etapas (nome/cor/ordem) personalizáveis.

### Renovações
Controle de vencimentos e status (pendente/contatado/renovado/perdido), com
alertas de renovações próximas e vencidas.

### Agentes, Produtores e Comissões
Hierarquia agente → produtor; cálculo de repasses de comissões (corretora,
agente, produtor).

### Relatórios
Exportação em **PDF** e **CSV** de: clientes, seguradoras, apólices, propostas,
sinistros, renovações, comissões e carteira.

### IA — Resumos
Botão "Resumir com IA" em cliente, apólice, sinistro, proposta e negociação.
Dispara task assíncrona que salva o resumo em `ai_summary` e cria notificação.

### IA — Chat
Chat com sessões salvas por usuário, resposta em **stream (SSE)** e renderização
de **Markdown sanitizado**.

### Notificações
Sino no topo com contador de não lidas; "marcar como lidas".

### Admin
Painel Django com todas as entidades, filtros por corretora (exceto superuser)
e integração com **dj-celery-panel** para inspecionar tasks.
