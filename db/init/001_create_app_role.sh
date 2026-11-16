#!/bin/sh
set -eu
psql --set=ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  --set=app_password="$TETHER_APP_PASSWORD" \
  --file /app-init/001_create_app_role.sql
