#!/bin/bash

set -x
echo "Starting Image Service ..."

echo "Starting Redis"
redis-server --daemonize yes

echo "Starting Celery"
celery -A src.tasks worker --loglevel=info &

echo "Starting uvicorn"
uvicorn src.main:app --host 0.0.0.0 --port 8000
