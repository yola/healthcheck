SECRET_KEY = 'None'
ROOT_URLCONF = 'healthcheck.contrib.django.status_endpoint.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'mydatabase',
    }
}
