# apps.py in your lms app
from django.apps import AppConfig

class LmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lms'
    
    def ready(self):
        # Import signals to register them
        import lms.signals  # Replace with your actual app name
