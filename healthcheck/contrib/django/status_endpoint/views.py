import json

from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, HttpResponseServerError

from healthcheck.healthcheck import (
    DjangoDBsHealthCheck, FilesDontExistHealthCheck, HealthChecker)


@require_http_methods(['GET'])
def status(request):
    checks = []

    if getattr(settings, 'STATUS_CHECK_DBS', True):
        checks.append(DjangoDBsHealthCheck())

    files_to_check = getattr(
        settings, 'STATUS_CHECK_FILES')
    if files_to_check:
        checks.append(
            FilesDontExistHealthCheck(
                files_to_check, check_id="quiesce file doesn't exist"))

    ok, details = HealthChecker(checks)()

    if not ok:
        return HttpResponseServerError((json.dumps(details)))

    return HttpResponse(json.dumps(details))
