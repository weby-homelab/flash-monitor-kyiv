#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
# Run with 1 worker to avoid multiple monitor threads race condition
exec gunicorn --workers 1 --threads 8 -b 0.0.0.0:5050 app:app --daemon
