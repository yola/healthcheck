import abc
import os.path


class HealthCheck(object):
    """Base class for all checks."""

    __metaclass__ = abc.ABCMeta

    check_id = None

    def __init__(self, is_critical=True, check_id=None):
        """Possible arguments:

            - check_id: ID of check. It overrides class-level check_id. If it's
                not defined neither at class level nor here, the error is
                raised.
            - is_critical: True/False. If True and check is failed, overall
                system health considered as "NOT ok". Otherwise,
        """
        self.is_critical = is_critical

        if check_id:
            self.check_id = check_id

        if self.check_id is None:
            raise ValueError('You must specify check_id for the check %s.' %
                             (self,))

        self._ok = None
        self._details = {}

    @abc.abstractmethod
    def run(self):
        """If you create your own HealthCheck, it should implement .run()
        method, which sets self._ok and self._details properties."""
        pass

    @property
    def is_ok(self):
        if self._ok is None:
            raise RuntimeError(
                'You must call .run() first. And your run() must '
                'set self._ok and self._details properties')
        return self._ok

    @property
    def details(self):
        # Just to verify that .run() is called.
        self.is_ok
        return self._details

    def as_dict(self):
        return {'status': 'ok' if self.is_ok else 'FAILED',
                'details': self.details}


class ListHealthCheck(HealthCheck):
    """Base class for checks, which verify list of items in one check.

    Usage:
    ------
        See examples are below - DjangoDBsHealthCheck and FilesExistHealthCheck
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, items=None, **kwargs):
        super(ListHealthCheck, self).__init__(**kwargs)

        if not items and not self.items:
            raise ValueError('You have to specify items inside class or '
                             'pass items list on on object construction')

        self._items = items if items is not None else self.items

    def run(self):
        self._ok = True
        self._details = {}

        for item in self._items:
            item_ok, item_details = self.check_item(item)
            if not item_ok:
                self._ok = False

            self._details.update(item_details)

    @abc.abstractmethod
    def check_item(self, item):
        """ This is called to check each item. It must return the following:
        <item_check_status>, {<item_id>: <item_check_details}

        Examples:
            False, {'my_first_db': 'No Connection!'};
            True, {'file /etc/passwd': 'file exists'}
        """


class DjangoDBsHealthCheck(ListHealthCheck):
    """Fails if at least one of configured Django DBs is not usable."""

    check_id = 'Django Databases Health Check'

    @property
    def items(self):
        from django.db import connections
        return connections.all()

    def check_item(self, connection):
        connection.ensure_connection()
        db_ok = connection.is_usable()
        details = {connection.alias: 'ok' if db_ok else 'FAILED'}
        return db_ok, details


class FilesExistHealthCheck(ListHealthCheck):
    """Fails if at least one of passed files doesn't exist."""

    def check_item(self, filename):
        file_exists = os.path.isfile(filename)
        details = {filename: 'exists' if file_exists else 'NO SUCH FILE'}
        return file_exists, details


class FilesDontExistHealthCheck(ListHealthCheck):
    """Fails if at least one of passed files exists."""

    def check_item(self, filename):
        file_exists = os.path.isfile(filename)
        details = {filename: 'FILE EXISTS' if file_exists else 'no such file'}
        return not file_exists, details


class HealthChecker(object):
    """Health Checker class.

    Usage:

        system_health_checker = HealthChecker([
             DjangoDBHealthCheck(),
             FilesExistHealthCheck(('/etc/passwd', '/var/run/apache.run'),
             FilesDontExistHealthCheck(('/var/tmp/EMERGENCY',))
        ])

        system_health_ok, details = system_health_checker()
    """

    def __init__(self, checks):
        self._checks = self._validate_checks(checks)

    def _validate_checks(self, checks):
        for check in checks:
            if not isinstance(check, HealthCheck):
                raise ValueError(
                    'HealthChecker requires a list of '
                    'HealthCheck subclasses, {0} passed'.format(check))

        if len(set([c.check_id for c in checks])) < len(checks):
            raise ValueError('Duplicate check IDs detected.')

        return checks

    def __call__(self):
        overall_details = {}
        for check in self._checks:
            check.run()
            overall_details.update({check.check_id: check.as_dict()})

        overall_status = self._assess_overall_status()
        return overall_status, overall_details

    def _assess_overall_status(self):
        failed_checks = [check for check in self._checks if not check.is_ok]
        failed_critical_checks = [
            check for check in failed_checks if check.is_critical]

        # If any of critical checks failed, or all checks failed, system state
        # is False (means "bad").
        if failed_critical_checks or len(failed_checks) == len(self._checks):
            return False

        return True
