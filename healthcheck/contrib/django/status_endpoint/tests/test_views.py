import json
import os

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import connections
from django.test import TestCase, override_settings
from django.test.client import RequestFactory

from healthcheck.contrib.django.status_endpoint import views


if not settings.configured:
    settings.configure(
        DATABASE_ENGINE='sqlite3',
        DATABASES={
            'default': {
                'NAME': ':memory:',
                'ENGINE': 'django.db.backends.sqlite3',
                'TEST_NAME': ':memory:',
            },
        },
        DATABASE_NAME=':memory:',
        TEST_DATABASE_NAME=':memory:',
        INSTALLED_APPS=['healthcheck.contrib.django.status_endpoint'],
        ROOT_URLCONF='',
        DEBUG=False,
        SITE_ID=1,
        TEMPLATE_DEBUG=True,
        PROJECT_ROOT=os.path.dirname(os.path.abspath(__file__)),
        ALLOWED_HOSTS=['*'],
    )


class StatusEndpointViewsTestCase(TestCase):
    urls = 'healthcheck.contrib.django.status_endpoint.urls'

    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(
        STATUS_CHECK_DBS=True,
        STATUS_CHECK_FILES=('/etc/quiesce',)
    )
    def test_default_checks(self):
        request = self.factory.get(reverse(views.status))
        response = views.status(request)
        self.assertEqual(response.status_code, 200)

    @override_settings(
        STATUS_CHECK_DBS=True,
        STATUS_CHECK_FILES=()
    )
    def test_dont_check_files(self):
        request = self.factory.get(reverse(views.status))
        response = views.status(request)
        response_json = json.loads(response.content)
        self.assertTrue(
            "quiesce file doesn't exist" not in response_json)
        self.assertTrue(
            'Django Databases Health Check' in response_json)
        db_names = response_json['Django Databases Health Check']['details']
        self.assertTrue(
            all(connection.alias in db_names
                for connection in connections.all()))
        self.assertEqual(response.status_code, 200)

    @override_settings(
        STATUS_CHECK_DBS=False,
        STATUS_CHECK_FILES=()
    )
    def test_no_checks_raises_200(self):
        request = self.factory.get(reverse(views.status))
        response = views.status(request)
        response = {
            'content': json.loads(response.content),
            'status': response.status_code,
            }

        expected_response = {
            'content': 'There were no checks.',
            'status': 200,
        }

        self.assertEqual(response, expected_response)

