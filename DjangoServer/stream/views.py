from django.shortcuts import render
from .models import Stream

# Create your views here.
def index(request):
    latest_streams = Stream.objects.order_by('-pub_date')[:5]
    context = {'latest_streams' : latest_streams}
    return render(request, "stream/index.html", context);

def stream(request, stream_id):
    pass
