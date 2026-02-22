#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
# Run with multiple workers for high load performance
exec gunicorn --workers 4 --threads 4 -b 0.0.0.0:5050 app:app --daemon
