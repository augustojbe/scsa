#!/usr/bin/env bash
#
# scripts/deploy.sh — Deploy completo do SCSI em produção (Docker Swarm).
# Uso: sudo ./scripts/deploy.sh [--skip-build]
#
# Ciclo: .env seguro -> validações -> git pull -> build -> push -> stack deploy -> rollout.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

ENV_FILE="${ENV_FILE:-$PROJECT_DIR/.env.production}"
IMAGE="${IMAGE:-ghcr.io/pycodebr/scsi_v1}"
STACK_NAME="${STACK_NAME:-scsi_v1}"
SKIP_BUILD=0

if [[ "${1:-}" == "--skip-build" ]]; then
    SKIP_BUILD=1
fi

# Parser seguro de .env (KEY=VALUE), sem source/dot para não quebrar com &, $, *, @.
load_env() {
    local file="$1"
    if [[ ! -f "$file" ]]; then
        echo "ERRO: arquivo de ambiente não encontrado: $file" >&2
        exit 1
    fi
    while IFS='=' read -r key value; do
        key="${key%%[[:space:]]*}"
        [[ -z "$key" || "$key" == \#* ]] && continue
        # remove aspas simples/duplas do valor e espaços ao redor
        value="${value%%[[:space:]]*}"
        value="${value%\"*}"
        value="${value#\"}"
        value="${value%\'*}"
        value="${value#\'}"
        export "$key=$value"
    done < "$file"
}

load_env "$ENV_FILE"

fail() { echo "ERRO: $*" >&2; exit 1; }

echo "==> Validando pré-condições"

# 1. DEBUG deve ser False
[[ "${DEBUG:-True}" == "True" ]] && fail "DEBUG=True não é permitido em produção."
echo "    DEBUG=False OK"

# 2. localhost/127.0.0.1 em ALLOWED_HOSTS (healthcheck interno)
[[ "${ALLOWED_HOSTS:-}" == *"localhost"* ]] || fail "ALLOWED_HOSTS precisa conter 'localhost'."
echo "    ALLOWED_HOSTS OK"

# 3. Swarm ativo
docker info 2>/dev/null | grep -q "Swarm: active" || fail "Docker Swarm não está ativo."
echo "    Swarm ativo OK"

# 4. Secret Cloudflare
docker secret ls 2>/dev/null | grep -q "CLOUDFLARE_DNS_API_TOKEN" || fail "Secret CLOUDFLARE_DNS_API_TOKEN ausente."
echo "    Secret CLOUDFLARE_DNS_API_TOKEN OK"

# 5. Redes overlay
docker network ls 2>/dev/null | grep -q "traefik_public" || fail "Rede traefik_public ausente."
docker network ls 2>/dev/null | grep -q "scsi_v1_egress" || fail "Rede scsi_v1_egress ausente."
echo "    Redes overlay OK"

echo "==> git pull"
git pull

if [[ "$SKIP_BUILD" == "0" ]]; then
    echo "==> Build e push da imagem"
    docker build -t "${IMAGE}:latest" -f Dockerfile .
    SHA="$(git rev-parse --short HEAD)"
    docker tag "${IMAGE}:latest" "${IMAGE}:${SHA}"
    docker push "${IMAGE}:latest"
    docker push "${IMAGE}:${SHA}"
else
    echo "==> --skip-build: pulando build/push"
fi

echo "==> Deploy do stack"
docker stack deploy -c docker-stack.yml --with-registry-auth "$STACK_NAME"

echo "==> Forçando rollout de app, celery_worker e celery_beat"
docker service update --force "${STACK_NAME}_app" || true
docker service update --force "${STACK_NAME}_celery_worker" || true
docker service update --force "${STACK_NAME}_celery_beat" || true

echo "==> Deploy concluído."
