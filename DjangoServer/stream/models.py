from django.db import models

# Create your models here.
class Stream(models.Model):
    #author = models.ForeignKey('auth.User')
    stream_link = models.CharField(max_length=200)
    title = models.CharField(max_length=100)
    pub_date = models.DateTimeField('date published')
    description = models.TextField()
    
