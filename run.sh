#!/bin/sh
cd /app
apt-get update
apt-get install --yes ffmpeg libsm6 libxext6 vim tmux
pip3 install torch==1.12.1 torchvision --extra-index-url https://download.pytorch.org/whl/cu116
pip3 install -r requirements.txt
cd /app/LAVIS
pip3 install .
cd /app/
python3 run_backend.py
