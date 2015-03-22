from django.shortcuts import render, RequestContext, Http404, HttpResponseRedirect, HttpResponse
from profiles.models import UserProfile, Location

def home(request):
    location = Location.objects.get(id=1)
    if request.user.is_anonymous():
        template = 'customer_home.html'
        MyUser = None
        context = {
            'MyUser': MyUser,
            'location': location,
        }
        return render(request, template, context)
    
    elif request.user.userprofile.role != 'customer':
        template = 'customer_home.html'
        print request.user.userprofile.first_name
        print request.user.userprofile.role
        return HttpResponseRedirect('orders/company_home')
        MyUser = request.user.userprofile.first_name
        print request.user.userprofile.role
        context = {
            'MyUser': MyUser,
            'location': location,
        }
        return render(request, template, context)
    
    elif request.user.userprofile.role == 'customer':
        template = 'customer_home.html'
        MyUser = request.user.userprofile.first_name
        print request.user.userprofile.role
        context = {
            'MyUser': MyUser,
            'location': location,
        }
        return render(request, template, context)