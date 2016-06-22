from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'
urlpatterns = [
    url(r'^login$', auth_views.login, {'template_name' : 'accounts/login.html', 'extra_context' : {'next' : '/'}}, name='login'),
    url(r'^register$', views.RegisterView.as_view(), name='register'),
    url(r'^logout$', auth_views.logout, {'next_page' : '/'},  name='logout'),
    url(r'^profile', views.profile, name='profile')
]
