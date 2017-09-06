import os

import django


os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE', 'healthcheck.contrib.django.status_endpoint.settings')
django.setup()
