import json
import os
from threading import Thread
from unittest import skipIf


from django.core.urlresolvers import reverse
from django.db import connections
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings

from healthcheck.checks import DjangoDBsHealthCheck
from healthcheck.contrib.django.status_endpoint import views


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
        response_json = json.loads(response.content.decode())
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
            'content': json.loads(response.content.decode()),
            'status': response.status_code,
        }

        expected_response = {
            'content': 'There were no checks.',
            'status': 200,
        }

        self.assertEqual(response, expected_response)

    @override_settings(
        STATUS_CHECK_DBS=False,
        STATUS_CHECK_FILES=('/usr/bin/env',)
    )
    def test_failed_check(self):
        request = self.factory.get(reverse(views.status))
        response = views.status(request)
        response = {
            'content': json.loads(response.content.decode()),
            'status': response.status_code,
        }

        expected_response = {
            'content': {
                "quiesce file doesn't exist": {
                    'details': {
                        '/usr/bin/env': 'FILE EXISTS'
                    },
                    'status': 'FAILED'
                }
            },
            'status': 500,
        }

        self.assertEqual(response, expected_response)

    @override_settings(
        STATUS_CHECK_DBS=True,
        STATUS_CHECK_FILES=()
    )
    @skipIf('MYSQL_HOST' not in os.environ, 'Test requires MySQL')
    def test_dbs_thread_local(self):
        ddb = DjangoDBsHealthCheck()
        threads = []
        request = self.factory.get(reverse(views.status))
        response = views.status(request)

        for i in range(100):
            thread = Thread(target=ddb.run)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()  # Wait for request to be handled

        request = self.factory.get(reverse(views.status))
        response = views.status(request)
        self.assertEqual(response.status_code, 200)
