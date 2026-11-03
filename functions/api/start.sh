#!/bin/sh
set -e

python3 -m pip install --user -r requirements.txt
exec python3 main.py
