#!/bin/bash
cd '/home/f1red/Desktop/INPT/Stage INE1/stage-RAG/backend'
"/home/f1red/Desktop/INPT/Stage INE1/stage-RAG/.venv/bin/uvicorn" app:app --host 127.0.0.1 --port 8001 --log-level info
