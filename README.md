HealthCheck
===========

Classes and Django apps, which help Yola services do health checks.

Using the library directly:
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

Using the Django app:
--------------------
1. Add 'status' to your INSTALLED_APPS setting like this:

```
    INSTALLED_APPS = (
        ...
        'healthcheck.contrib.django.status_endpoint',
    )
```

2. Include the polls URLconf in your project urls.py like this:

```
    from healthcheck.contrib.django import status_endpoint
    url_patterns += url(r'^status/', status_endpoint.urls())
```

3. Visit http://127.0.0.1:8000/status/ to see the output of the healthchecks.

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

Running Tests
-------------

cd healthcheck; nosetests
