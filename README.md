HealthCheck
===========

Classes, which help Yola service to implement health checks for themselves.

Example (from SBBE):
--------------------
```
from healthcheck import (
    HealthChecker, DjangoDBsHealthCheck, FilesDontExistHealthCheck)


class StatusView(View):

    checks = [
        DjangoDBsHealthCheck(),
        FilesDontExistHealthCheck(
            ('/etc/yola/quiesce',), check_id='quiesce file doesn\'t exist'),]

    def get(self, *args, **kwargs):
        ok, details = HealthChecker(self.checks)()

        if not ok:
            return HttpResponseServerError((json.dumps(details)))

        return HttpResponse(json.dumps(details))
```


As a result, URL handled by this view will return data like this:

```
{
    "Django Databases Health Check":
        {
            "status": "ok",
            "details": {
                            "default": "ok",
                            "usersites2": "ok",
                            "usersites1": "ok"
            }
          },

    "quiesce file doesn't exist":
        {
            "status": "ok",
            "details": {
                            "/etc/yola/quiesce": "no such file"
            }
        }
}
```
