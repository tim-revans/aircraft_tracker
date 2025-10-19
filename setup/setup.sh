#!/usr/bin/env bash
echo "🔧 Setting up virtual environment..."
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate
echo "📦 Installing dependencies..."
pip install -r requirements.txt
echo "🚀 Launching app..."
python main.py
