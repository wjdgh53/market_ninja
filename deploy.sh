#!/bin/bash

cd ~/market_ninja
git pull origin main
~/market_ninja/venv/bin/pip install -r requirements.txt
pkill -f "venv/bin/python app.py"
nohup ~/market_ninja/venv/bin/python app.py > log.txt 2>&1 &