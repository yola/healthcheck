import json

from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse

from healthcheck import (
    DjangoDBsHealthCheck, FilesDontExistHealthCheck, HealthChecker)


class JsonResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        kwargs.setdefault('content_type', 'application/json')
        data = json.dumps(data)
        super(JsonResponse, self).__init__(content=data, **kwargs)


class JsonResponseServerError(JsonResponse):
    status_code = 500


@require_http_methods(['GET'])
def status(request):
    checks = []

    if getattr(settings, 'STATUS_CHECK_DBS', True):
        checks.append(DjangoDBsHealthCheck())

    files_to_check = getattr(settings, 'STATUS_CHECK_FILES', None)
    if files_to_check:
        checks.append(FilesDontExistHealthCheck(
            files_to_check, check_id="quiesce file doesn't exist"))

    ok, details = HealthChecker(checks)()

    if ok and not details:
        details = 'There were no checks.'

    if not ok:
        return JsonResponseServerError(details)

    return JsonResponse(details)
