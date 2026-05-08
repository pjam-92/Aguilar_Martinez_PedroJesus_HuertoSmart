"""
WSGI config for miproyectodjango project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'miproyectodjango.settings')

application = get_wsgi_application()
