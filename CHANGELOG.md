# [Changelog](https://github.com/yola/healthcheck)

## 0.1.4
* Drop Python 3.4.
* Add support for Python 3.5 and 3.6.

## 0.1.3
* Support sharing DjangoDBsHealthCheck objects across threads.

## 0.1.2
* Added catching OperationalError exception for django dbs check.

## 0.1.0
* Removed Python 2.6 support, added Python 3.5 support.

## 0.0.7
* Updated requirements.txt to include funcsigs and restrict mock updates.
* Added default to prevent `AttributeError` if `STATUS_CHECK_FILES` setting is missing.

## 0.0.6
* Bump version in order to remove mistakenly added debug code that was never
  committed to git.

## 0.0.5
* Return Ok if there are not checks.

## 0.0.4
* Add `healthcheck.contrib.django.status_endpoint` contrib app, for easily
  using the library from a Django app.

## 0.0.3
* Fixed incorrect usage of @abstractmethod decorator. It doesn't work without
  __metaclass__ = abc.ABCMeta
* Added validation for duplicate check IDs inside one HealthChecker.

## 0.0.2
* New version to override broken one in YolaPI.

## 0.0.1
* First version. Ability to add HealthChecks for Yola Services.
