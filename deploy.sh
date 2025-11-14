#!/usr/bin/env bash
set -e
pip install -r requirements.txt
python3 SMS/manage.py migrate --noinput
python3 SMS/manage.py collectstatic --noinput