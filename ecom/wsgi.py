import os
from django.core.wsgi import get_wsgi_application

#settings_module = 'ecom.deployment' if 'WEBSITE_HOSTNAME' in os.environ else 'ecom.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom.settings')

application = get_wsgi_application()
