# [Changelog](https://github.com/yola/healthcheck)

## 0.0.3
* Fixed incorrect usage of @abstractmethod decorator. It doesn't work without
  __metaclass__ = abc.ABCMeta
* Added validation for duplicate check IDs inside one HealthChecker.

## 0.0.2
* New version to override broken one in YolaPI.

## 0.0.1
* First version. Ability to add HealthChecks for Yola Services.
