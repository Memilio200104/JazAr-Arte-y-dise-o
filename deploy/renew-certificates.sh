#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
docker compose --profile tls run --rm certbot renew --webroot -w /var/www/certbot --quiet
docker compose exec -T nginx nginx -t
docker compose exec -T nginx nginx -s reload
