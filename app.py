import os
import sys

# Add the SMS directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'SMS'))

# Import the WSGI application
from school_app.wsgi import application as app

# This allows Render to find the application when it looks for 'app:app'
