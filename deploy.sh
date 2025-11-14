#!/usr/bin/env bash
set -e
pip install -r requirements.txt
python SMS/manage.py migrate --noinput
python SMS/manage.py collectstatic --noinput