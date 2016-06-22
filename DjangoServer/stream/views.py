from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import FormView
from .models import Stream
from .forms import StreamForm
from .create_stream import create_stream

def index(request):
    latest_streams = Stream.objects.order_by('-pub_date')[:5]
    context = {'latest_streams' : latest_streams}
    return render(request, "stream/index.html", context);

def stream(request, stream_id):
    stream = get_object_or_404(Stream, id=stream_id)
    context = {'stream' : stream}
    return render(request, "stream/stream.html", context)

def all_streams(request):
    all_streams = Stream.objects.order_by('-pub_date')
    context = {'streams' : all_streams}
    return render(request, "stream/all_streams.html", context)


class CreateStreamView(FormView):
    form_class = StreamForm
    success_url = '/'
    template_name = 'stream/create_stream.html'

    def form_valid(self, form):
        stream = form.save(commit='false')
        stream.author = self.request.user
        stream.in_stream_link, stream.out_stream_link = \
                create_stream(stream.id)
        stream.save()
        return super(CreateStreamView, self).form_valid(form)
        
