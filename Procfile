release: python SMS/manage.py migrate && python SMS/manage.py collectstatic --noinput
web: gunicorn SMS.school_app.wsgi