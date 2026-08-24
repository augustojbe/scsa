#!/usr/bin/env bash
#
# scripts/backup.sh — Backup do PostgreSQL (pg_dump custom) + media (tarball),
# com rotação por tempo. Adequado para cron, ex.:
#   0 2 * * * /path/scripts/backup.sh >> /var/log/scsi-backup.log 2>&1
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

BACKUP_ROOT="${BACKUP_ROOT:-/backups}"
RETENTION_DAILY="${RETENTION_DAILY:-7}"
RETENTION_WEEKLY="${RETENTION_WEEKLY:-4}"

STACK_NAME="${STACK_NAME:-scsi_v1}"
DB_USER="${DB_USER:-scsi}"
DB_NAME="${DB_NAME:-scsi}"

TODAY="$(date +%F)"
WEEK="$(date +%G-W%V)"
STAMP="$(date +%F_%H%M%S)"

DB_DIR="$BACKUP_ROOT/db"
MEDIA_DIR="$BACKUP_ROOT/media"
mkdir -p "$DB_DIR" "$MEDIA_DIR"

DB_FILE="$DB_DIR/${DB_NAME}_${STAMP}.dump"
MEDIA_FILE="$MEDIA_DIR/media_${STAMP}.tar.gz"

echo "==> Backup em $BACKUP_ROOT ($(date))"

echo "==> pg_dump (custom)"
DB_ID="$(docker service ps -q --filter desired-state=running "${STACK_NAME}_db" 2>/dev/null | head -n1 || true)"
if [[ -n "$DB_ID" ]]; then
    CONTAINER="${STACK_NAME}_db.1.$(echo "$DB_ID" | cut -c1-12)"
    echo "    Usando container: $CONTAINER"
    docker exec "$CONTAINER" pg_dump -U "$DB_USER" -F c -b -d "$DB_NAME" > "$DB_FILE"
else
    echo "    Aviso: serviço db sem réplica em execução; usando pg_dump local." >&2
    pg_dump -U "$DB_USER" -F c -b -d "$DB_NAME" > "$DB_FILE"
fi
echo "    OK: $DB_FILE"

echo "==> media (tarball)"
if [[ -d "$PROJECT_DIR/media" ]]; then
    tar -czf "$MEDIA_FILE" -C "$PROJECT_DIR" media
    echo "    OK: $MEDIA_FILE"
else
    echo "    Aviso: pasta media não encontrada; pulando." >&2
    rm -f "$MEDIA_FILE"
fi

# Rotações
echo "==> Rotação"
# Diário: manter os N arquivos mais recentes por data (diários)
ls -1t "$DB_DIR"/*.dump 2>/dev/null | tail -n +$((RETENTION_DAILY + 1)) | xargs -r rm -f
ls -1t "$MEDIA_DIR"/*.tar.gz 2>/dev/null | tail -n +$((RETENTION_DAILY + 1)) | xargs -r rm -f

# Semanal: manter apenas o backup de cada semana (não excluídos acima)
# (rotina simples de retenção; pode ser estendida conforme necessidade)

echo "==> Backup concluído com sucesso."
