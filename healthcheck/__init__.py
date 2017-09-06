__doc__ = 'Health Checker for Yola Services'
__version__ = '0.0.7'
__url__ = 'https://github.com/yola/healthcheck'

ROOT_URLCONF = ''
from .healthcheck import (HealthChecker, HealthCheck, ListHealthCheck,
                         DjangoDBsHealthCheck, FilesExistHealthCheck,
                         FilesDontExistHealthCheck)
