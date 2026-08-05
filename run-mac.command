#!/bin/bash
# GDC Production Manager — quick launcher (run from source, Mac/Linux)
cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
else
  source venv/bin/activate
fi

python backend/app.py
