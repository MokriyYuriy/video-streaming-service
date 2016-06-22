from django.views.generic.edit import FormView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from stream.models import Stream

class RegisterView(FormView):
    form_class = UserCreationForm
    success_url = '/account/login'
    template_name = 'accounts/register.html'
    
    def form_valid(self, form):
        form.save()
        return super(RegisterView, self).form_valid(form)

@login_required
def profile(request):
    my_streams = Stream.objects.filter(author=request.user).order_by('-pub_date')
    context = {'my_streams' : my_streams}
    return render(request, 'accounts/profile.html', context)
