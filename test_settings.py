import os

SECRET_KEY = 'None'
ROOT_URLCONF = 'healthcheck.contrib.django.status_endpoint.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'mydatabase',
    },
}

# pg_virtualenv:
if 'PGHOST' in os.environ:
    DATABASES['postgres'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.environ['PGHOST'],
        'PORT': os.environ['PGPORT'],
        'NAME': os.environ['PGDATABASE'],
        'USER': os.environ['PGUSER'],
        'PASSWORD': os.environ['PGPASSWORD'],
    }

# my_virtualenv:
if 'MYSQL_HOST' in os.environ:
    DATABASES['mysql'] = {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': os.environ['MYSQL_HOST'],
        'NAME': 'test',
    }
