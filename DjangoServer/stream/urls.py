from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from . import views

app_name = "stream"
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<stream_id>[0-9]+)/$', views.stream, name='stream'),
    url(r'^create_stream$', login_required(views.CreateStreamView.as_view()), name='create_stream'),
    url(r'^all_streams/$', views.all_streams, name='all_streams')
]
