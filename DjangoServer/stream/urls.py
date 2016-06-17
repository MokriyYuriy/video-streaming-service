from django.conf.urls import url

from . import views

app_name = "stream"
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<stream_id>[0-9]+)/$', views.stream, name='stream'),
]
