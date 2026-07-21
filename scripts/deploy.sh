#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/opt/habit_tracker_backend}"
cd "$PROJECT_DIR"

if [[ ! -f .env ]]; then
    echo "Deployment failed: $PROJECT_DIR/.env does not exist." >&2
    exit 1
fi

docker compose config --quiet
docker compose up -d --build --remove-orphans

HTTP_PORT="$(sed -n 's/^HTTP_PORT=//p' .env | tail -n 1 | tr -d '\r')"
HTTP_PORT="${HTTP_PORT:-80}"

for attempt in $(seq 1 36); do
    if curl --fail --silent --show-error \
        "http://127.0.0.1:${HTTP_PORT}/health/" >/dev/null; then
        docker compose exec -T web python manage.py check
        docker compose ps --all
        docker image prune -f
        echo "Deployment completed successfully."
        exit 0
    fi

    echo "Waiting for production health check: ${attempt}/36"
    sleep 5
done

echo "Deployment health check failed." >&2
docker compose ps --all
docker compose logs --no-color --tail=300
exit 1
