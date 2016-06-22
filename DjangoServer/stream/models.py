from django.db import models
from django.contrib.auth.models import User

class Stream(models.Model):
    author = models.ForeignKey(User, default=1)
    in_stream_link = models.CharField(max_length=200, null=True)
    out_stream_link = models.CharField(max_length=200)
    title = models.CharField(max_length=100)
    pub_date = models.DateTimeField('date published', auto_now_add=True, blank=True)
    description = models.TextField()
    
class RTSPServer(models.Model):
    address = models.CharField(max_length=200)
