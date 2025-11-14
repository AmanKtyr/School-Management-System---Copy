#!/usr/bin/env bash

pip install -r requirements.txt
python SMS/manage.py migrate --noinput
python SMS/manage.py collectstatic --noinput