release: python manage.py migrate
web: gunicorn school_app.wsgi --bind 0.0.0.0:$PORT