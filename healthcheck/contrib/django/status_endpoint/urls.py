from django.conf.urls import url

from healthcheck.contrib.django.status_endpoint.views import status

urlpatterns = [
    url(r'^$', status),
]
