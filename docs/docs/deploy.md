# Deploy

## Produção com Docker Swarm

Imagem publicada em `ghcr.io/pycodebr/scsi_v1`.

### 1. Preparar a VPS

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose-plugin
sudo systemctl enable --now docker
docker swarm init --advertise-addr <VPS_IP>
```

### 2. Criar redes overlay

```bash
docker network create --driver overlay --attachable traefik_public
docker network create --driver overlay --internal scsi_v1_internal
docker network create --driver overlay scsi_v1_egress
```

### 3. Secrets

```bash
echo "<CLOUDFLARE_TOKEN>" | docker secret create CLOUDFLARE_DNS_API_TOKEN -
echo "<SECRET_KEY>"        | docker secret create DJANGO_SECRET_KEY -
echo "<POSTGRES_PASSWORD>" | docker secret create POSTGRES_PASSWORD -
echo "<OPENAI_API_KEY>"    | docker secret create OPENAI_API_KEY -
```

### 4. Deploy

```bash
./scripts/deploy.sh            # build + push + stack deploy + rollout
./scripts/deploy.sh --skip-build
```

Ou manualmente:

```bash
docker stack deploy -c docker-stack.yml --with-registry-auth scsi_v1
```

### 5. Backup

```bash
./scripts/backup.sh
# agendar via cron, ex.: 0 2 * * * /path/scripts/backup.sh
```

## Resiliência

- Healthchecks em todos os serviços (app via `/health/`, sem banco e sem auth).
- `restart_policy: on-failure` em todos os serviços.
- `resources.limits`/`reservations` de CPU/memória.
- App com `update_config`: `order: start-first`, `failure_action: rollback` —
  rollback automático se a réplica nova falhar no healthcheck.
- Entrypoints com `wait_for_db` evitam crash-loop por dependência não pronta.

## Migrations e staticfiles

- O entrypoint do app executa `wait_for_db` → migrations com advisory lock →
  `collectstatic --clear` → gunicorn.
- Celery apenas executa `wait_for_db` (sem migrations/collectstatic).
