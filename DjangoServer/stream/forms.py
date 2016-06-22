from django.db import models
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from .models import Stream


class StreamForm(ModelForm):
    class Meta:
        model = Stream
        fields = ('title', 'description')
        labels = {'title' : _('Stream name'),
                  'description' : _('Brief description')}
