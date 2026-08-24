# Instalação

## Pré-requisitos

- Python 3.13+
- Docker + Docker Compose (para o ambiente local containerizado)
- PostgreSQL, RabbitMQ e Redis (se rodar sem Docker)

## Ambiente local com Docker Compose

```bash
# 1. Configure o .env
cp .env.example .env   # ou crie manualmente conforme .env

# 2. Suba os serviços
docker compose up --build

# 3. Aplique migrações e carregue dados fake (uma vez)
docker compose exec app python manage.py migrate
docker compose exec app python manage.py load_fake_data
```

A aplicação fica em `http://localhost:8000` (saúde em `/health/`).

## Ambiente local sem Docker

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# gere o .env (DEBUG=True, DATABASE_URL sqlite:///db.sqlite3)
python manage.py migrate
python manage.py load_fake_data
python manage.py runserver
```

## Variáveis de ambiente

| Variável | Descrição |
|---|---|
| `DEBUG` | True em dev, False em produção |
| `SECRET_KEY` | Chave secreta do Django |
| `ALLOWED_HOSTS` | Hosts permitidos (separados por vírgula) |
| `CSRF_TRUSTED_ORIGINS` | Origens confiáveis (separadas por vírgula) |
| `DATABASE_URL` | URL de conexão do banco |
| `REDIS_URL` | URL do Redis (cache + result backend) |
| `CELERY_BROKER_URL` | URL do RabbitMQ (broker) |
| `OPENAI_API_KEY` | Chave da OpenAI (opcional; sem ela há fallback simulado) |
| `OPENAI_MODEL` | Modelo (padrão `gpt-5.5-mini`) |

## Dados fake

```bash
python manage.py load_fake_data
```

Cria uma corretora de demonstração com usuários, clientes, seguradoras, ramos,
coberturas, propostas, apólices, sinistros, renovações, endossos, agentes,
produtores, comissões e pipeline de CRM.
