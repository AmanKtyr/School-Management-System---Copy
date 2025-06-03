import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "school_app.settings")
django.setup()

from django.db import connection

# SQL to create auth_user table
create_auth_user_sql = """
CREATE TABLE IF NOT EXISTS auth_user (
    id SERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE NULL,
    is_superuser BOOLEAN NOT NULL,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_staff BOOLEAN NOT NULL,
    is_active BOOLEAN NOT NULL,
    date_joined TIMESTAMP WITH TIME ZONE NOT NULL
);
"""

# Execute the SQL
with connection.cursor() as cursor:
    cursor.execute(create_auth_user_sql)
    print("auth_user table created successfully")
