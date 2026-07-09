#!/bin/bash

uv run src/startup.py
exec uvicorn src.main:app --host 0.0.0.0 --port 1210 --workers 4 --log-config /home/huc/huc-editor-service/conf/log-config.yaml