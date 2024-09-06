#!/bin/bash

set -e

if [ ! -f .env ]; then
  echo ".env file not found! Please create the .env file before running this script."
  exit 1
fi

docker compose -f docker-prod.yml down

git pull


docker compose -f docker-prod.yml up -d

docker exec -it sb_backend sh -c "python manage.py collectstatic"
docker exec -it sb_backend sh -c "python manage.py migrate"

echo "done"