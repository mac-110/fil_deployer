#!/bin/sh

# Start FastAPI backend in background
cd /app
python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 &

# Start Nginx in foreground
nginx -g 'daemon off;'

