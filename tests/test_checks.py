# -*- coding: utf-8 -*-
import errno
from tempfile import NamedTemporaryFile
from unittest import TestCase

from django.db import OperationalError
from mock import Mock, patch

from healthcheck.checks import (
    DjangoDBsHealthCheck,
    FilesDontExistHealthCheck,
    FilesExistHealthCheck,
    HealthCheck,
    HealthChecker,
    ListHealthCheck,
)


class MyCheck(HealthCheck):
    check_id = 'test_check_id'

    def run(self):
        self._ok = self.mock_ok
        self._details = self.mock_details


class TestHealthCheck(TestCase):

    def setUp(self):
        self.check = MyCheck()

    def test_cant_create_healthcheck_without_run_method(self):
        class MyCheck(HealthCheck):
            check_id = 'check_id'

        self.assertRaisesRegexp(
            ValueError,
            'You must override "run" method for check MyCheck', MyCheck().run
        )

    def test_cant_create_healthcheck_without_id(self):
        class MyCheck(HealthCheck):
            def run(self):
                pass

        self.assertRaisesRegexp(ValueError, 'You must specify check_id',
                                MyCheck)

    def test_check_id_is_overriden_by_init_param(self):
        check = MyCheck(check_id='new check id')
        self.assertEqual(self.check.check_id, 'test_check_id')
        self.assertEqual(check.check_id, 'new check id')

    def test_cant_access_check_status_before_run(self):
        self.assertRaisesRegexp(
            RuntimeError, 'You must call \.run\(\) first',
            lambda: self.check.is_ok)

    def test_cant_access_check_details_before_run(self):
        self.assertRaisesRegexp(
            RuntimeError, 'You must call \.run\(\) first',
            lambda: self.check.details)

    def test_check_results_are_returned_correctly_if_check_succeeds(self):
        self.check.mock_ok = True
        self.check.mock_details = 'details'
        self.check.run()
        self.assertTrue(self.check.is_ok)
        self.assertEqual(self.check.details, 'details')

    def test_check_results_are_returned_correctly_if_check_fails(self):
        self.check.mock_ok = False
        self.check.mock_details = 'details'
        self.check.run()
        self.assertFalse(self.check.is_ok)
        self.assertEqual(self.check.details, 'details')

    def test_as_dict_works_correctly_if_check_succeeds(self):
        self.check.mock_ok = True
        self.check.mock_details = 'details'
        self.check.run()
        self.assertEqual(self.check.as_dict(), {'details': 'details',
                                                'status': 'ok'})

    def test_as_dict_works_correctly_if_check_fails(self):
        self.check.mock_ok = False
        self.check.mock_details = 'details'
        self.check.run()
        self.assertEqual(self.check.as_dict(), {'details': 'details',
                                                'status': 'FAILED'})


class MyListHealthCheck(ListHealthCheck):
    check_id = 'test_list_check_id'

    @property
    def items(self):
        return self.mock_items

    def check_item(self, item):
        return True, {}


class TestListHealthCheck(TestCase):

    def test_cannot_create_check_without_items(self):
        MyListHealthCheck.mock_items = None
        self.assertRaisesRegexp(ValueError,
                                'You have to specify items inside class',
                                MyListHealthCheck)

    def test_items_can_be_passed_in_runtime(self):
        MyListHealthCheck.mock_items = None
        # No exception raised - ok.
        MyListHealthCheck(items=(1, 2, 3))

    def test_returns_correct_result_for_all_items(self):
        MyListHealthCheck.mock_items = (1, 2, 3)
        check = MyListHealthCheck()
        check.mock_items = (1, 2, 3)
        check.check_item = lambda item: (True,
                                         {item: '{0} tested'.format(item)})
        check.run()
        self.assertEqual(check.is_ok, True)
        expected_details = dict([(item, '{0} tested'.format(item))
                                 for item in (1, 2, 3)])
        self.assertEqual(check.details, expected_details)

    def test_check_fails_if_at_least_check_for_one_item_fails(self):
        MyListHealthCheck.mock_items = (1, 2, 3)
        check = MyListHealthCheck()
        check.mock_items = (1, 2, 3)
        check.check_item = lambda item: (False if item == 2 else True, {})
        check.run()
        self.assertEqual(check.is_ok, False)


class TestFilesExistHealthCheck(TestCase):
    def test_ok_if_all_files_exist(self):
        tmpfile1 = NamedTemporaryFile()
        tmpfile2 = NamedTemporaryFile()
        file1 = tmpfile1.name
        file2 = tmpfile2.name
        check = FilesExistHealthCheck((file1, file2), check_id='checkid')
        check.run()
        self.assertTrue(check.is_ok)
        self.assertEqual(check.details, {file1: 'exists',
                                         file2: 'exists'})

    def test_not_ok_if_at_least_one_file_doesnt_exist(self):
        tmpfile1 = NamedTemporaryFile()
        file1 = tmpfile1.name
        check = FilesExistHealthCheck((file1, 'file2'), check_id='checkid')
        check.run()
        self.assertFalse(check.is_ok)
        self.assertEqual(check.details, {file1: 'exists',
                                         'file2': 'NO SUCH FILE'})


class TestFilesDontExistHealthCheck(TestCase):
    def test_ok_if_all_files_dont_exist(self):
        check = FilesDontExistHealthCheck(('file1', 'file2'),
                                          check_id='checkid')
        check.run()
        self.assertTrue(check.is_ok)
        self.assertEqual(check.details, {'file1': 'no such file',
                                         'file2': 'no such file'})

    def test_not_ok_if_at_least_one_file_exists(self):
        tmpfile2 = NamedTemporaryFile()
        file2 = tmpfile2.name
        check = FilesDontExistHealthCheck(('file1', file2),
                                          check_id='checkid')
        check.run()
        self.assertFalse(check.is_ok)
        self.assertEqual(check.details, {'file1': 'no such file',
                                         file2: 'FILE EXISTS'})


class TestFilesHealthCheckWithError(TestCase):
    @patch('os.stat')
    def test_error_when_checking_if_files_exist(self, stat_mock):
        stat_mock.side_effect = OSError(errno.EACCES, 'Permission denied')
        for check_type in (FilesExistHealthCheck, FilesDontExistHealthCheck):
            check = check_type(('file',), check_id='checkid')
            check.run()
            self.assertFalse(check.is_ok)
            self.assertEqual(check.details,
                             {'file': 'ERROR: Permission denied'})


class TestDjangoDBsHealthCheck(TestCase):

    @patch('django.db.connections')
    def test_returns_ok(self, connections_mock):
        connection_mock = Mock(alias='db_name')
        connections_mock.all.return_value = [connection_mock]
        check = DjangoDBsHealthCheck()
        check.run()
        self.assertTrue(check.is_ok)
        self.assertEqual(check.details, {'db_name': 'ok'})
        connection_mock.ensure_connection.assert_called_once_with()
        connection_mock.is_usable.assert_called_once_with()

    @patch('django.db.connections')
    def test_fails_when_ensure_connection_fail(self, connections_mock):
        connections_mock.all.return_value = [
            Mock(alias='db_name',
                 ensure_connection=Mock(side_effect=OperationalError()))
        ]
        check = DjangoDBsHealthCheck()
        check.run()
        self.assertFalse(check.is_ok)
        self.assertEqual(check.details, {'db_name': 'FAILED'})

    @patch('django.db.connections')
    def test_fails_when_connection_is_not_usable(self, connections_mock):
        connections_mock.all.return_value = [
            Mock(alias='db_name',
                 is_usable=Mock(return_value=False))
        ]
        check = DjangoDBsHealthCheck()
        check.run()
        self.assertFalse(check.is_ok)
        self.assertEqual(check.details, {'db_name': 'FAILED'})


class TestHealthChecker(TestCase):
    def setUp(self):
        self.check1 = MyCheck(check_id='check1')
        self.check1.mock_ok = True
        self.check1.mock_details = 'result1'

        self.check2 = MyCheck(check_id='check2')
        self.check2.mock_ok = True
        self.check2.mock_details = 'result2'

        self.check3 = MyCheck(check_id='check3', is_critical=False)
        self.check3.mock_ok = False
        self.check3.mock_details = 'result3'

        self.checker = HealthChecker([self.check1, self.check2, self.check3])

    def test_cannot_checks_ids_cannot_overlap(self):
        self.assertRaisesRegexp(ValueError, 'Duplicate check IDs detected',
                                HealthChecker, [MyCheck(check_id='111'),
                                                MyCheck(check_id='111')])

    def test_only_healthcheck_instances_are_accepted(self):
        self.assertRaisesRegexp(
            ValueError,
            'HealthChecker requires a list of HealthCheck subclasses',
            HealthChecker, ['something', MyCheck(check_id='111')])

    def test_all_checks_results_are_present_in_final_result(self):
        expected_result = {
            'check1': {'details': 'result1', 'status': 'ok'},
            'check2': {'details': 'result2', 'status': 'ok'},
            'check3': {'details': 'result3', 'status': 'FAILED'}
        }

        ok, details = self.checker()
        self.assertEqual(details, expected_result)

    def test_overall_status_is_ok_if_non_critical_check_failed(self):
        ok, details = self.checker()
        self.assertTrue(ok)

    def test_overall_status_is_failed_if_critical_check_failed(self):
        self.check1.mock_ok = False
        ok, details = self.checker()
        self.assertFalse(ok)
