#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python SMS/manage.py collectstatic --no-input
python SMS/manage.py migrate