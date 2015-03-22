from django.shortcuts import render, HttpResponseRedirect, render_to_response, Http404
from .forms import LoginForm, RegisterForm, ZipInput
from django.core.urlresolvers import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model, authenticate, login, logout
from .models import UserProfile, ZipData, User, Location
from django.views.generic import DetailView
from django.contrib.admin.views.decorators import staff_member_required
from django.template import RequestContext
import csv

from orders.models import Order

User = get_user_model()


##use active and inactive to set bans.
def mylogin(request):
    login_form = LoginForm(request.POST or None, initial={'form_tag':'login'})
    template = 'profiles/form.html'
    try:
        request.session['new_auth']
        new_auth = request.session['new_auth']
    except:
        new_auth = False
    try: 
        request.session['location']
        location_session = request.session['location']
        location = Location.objects.get(id=location_session)
    except:
        location = Location.objects.get(id=1)
        request.session['location'] = location.id   
    if login_form.is_valid():
        form = login_form
        try:

            order_id = str(request.session['order_id'])
            order = Order.objects.get(id=order_id).id
            street_address = str(request.session['street_address'])
            zipcode = str(request.session['zipcode'])
            city = str(request.session['city'])
            state = str(request.session['state'])
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(username=email,
                                password=password,
            )
            print 'authenticated'
            if user is not None:
                if user.is_active:
                    login(request, user)
                    request.user
                    return HttpResponseRedirect('/orders/%s' % order)
                else:
                    print inactive
                  
        
        
        except:
            print 'except chain started'
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(username=email,
                                password=password,
            )
            if user is not None:
                if user.is_active:
                    login(request, user)
                    request.user
                    return HttpResponseRedirect('/')
                else:
                    print inactive
    context = {
        'login_form': login_form,
        'new_auth':new_auth,
        'location': location,
    }
    return render(request, template, context)





def register(request):
    register_form = RegisterForm(request.POST or None, initial={'form_tag':'register'})
    login_form = LoginForm(request.POST or None, initial={'form_tag':'login'})
    template = 'profiles/form.html'
    new_auth = False
    MyUser = request.user
    print MyUser
    try:
        request.session['anonymous_user_id']
        print request.session['anonymous_user_id']
    except:
        print 'anony id not found'
    #try:
    
    if request.user.is_authenticated():
        print 'authenticated'
    else:
        print ' no auth'
    
    try: 
        request.session['location']
        print request.session['location']
        location_session = request.session['location']
        location = Location.objects.get(id=location_session)
    except:
        location = Location.objects.get(id=1)
        print location
        request.session['location'] = location.id
        print request.session['location']
    
    if request.method == 'POST':
        print request.POST
        if request.POST['form_tag'] == 'register':
            register_form = RegisterForm(request.POST)
            if register_form.is_valid():
                form = register_form
                form.save(commit=False)
                
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                username = form.cleaned_data['email']
                password = form.cleaned_data['password']
                phone = form.cleaned_data['phone']
                email = form.cleaned_data['email']
                try:
                    ###this is for when an anonymous user is rerouted
                    request.session['anonymous_user_id']
                    print 'anony id detected, updating anony user'
                    fake_id = request.session['anonymous_user_id']
                    default_user = User.objects.get(id=fake_id)
                    default_user.username = username
                    default_user.email = email
                    default_user.save()
                    profile, created = UserProfile.objects.get_or_create(
                                                    user_id=default_user.id,
                                                    first_name=first_name,
                                                    last_name=last_name,
                                                    phone=phone,
                                                    email=email
                    )
                    if created:
                        print 'profile created'
                    else:
                        print profile
                    b = User.objects.get(username=default_user.username)
                    print b.username
                    default_user.set_password(request.POST['password'])
                    print 'password set'
                    default_user.save()
                    request.session['new_auth'] = True
                    return HttpResponseRedirect('/login/')
                except:
                    print 'no anony id, making user from standard register'
                    default_user = User.objects.create_user(
                                   username, email, password
                    )
                    profile = UserProfile.objects.create(
                                                        user=default_user,
                                                        first_name=first_name,
                                                        last_name=last_name,
                                                        phone=phone,
                                                        email=email
                    )
                    user = authenticate(username=username,
                                        password=password,
                                        email=email)
                    user.set_password(request.POST['password'])
                    user.save()
                    login(request, user)
                    return HttpResponseRedirect('/login/')

        elif request.POST['form_tag'] == 'login':
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                form = login_form
                try:
                    
                    street_address = str(request.session['street_address'])
                    zipcode = str(request.session['zipcode'])
                    city = str(request.session['city'])
                    state = str(request.session['state'])
                    email = form.cleaned_data['email']
                    password = form.cleaned_data['password']
                    user = authenticate(username=email,
                                        password=password,
                    )
                    print user
                    print 'user id %s' % user.id
                    print 'MyUser id %s' % MyUser.id
                    order_id = str(request.session['order_id'])
                    order = Order.objects.get(id=order_id)
                    print order
                    order.customer_id = user.id
                    order.save()
                    print 'order customer id %s '%order.customer_id
                    
                    if user is not None:
                        if user.is_active:
                            login(request, user)
                            request.user
                            return HttpResponseRedirect('/orders/%s' % order.id)
                        else:
                            print inactive
                          
                
                
                except:
                    print 'except chain started'
                    email = form.cleaned_data['email']
                    password = form.cleaned_data['password']
                    user = authenticate(username=email,
                                        password=password,
                    )
                    if user is not None:
                        if user.is_active:
                            login(request, user)
                            request.user
                            return HttpResponseRedirect('/')
                        else:
                            print inactive

    context = {
        'register_form': register_form,
        'login_form': login_form,
        'location': location,
        'new_auth':new_auth,
    }
    return render(request, template, context)





def mylogout(request):
    logout(request)
    return HttpResponseRedirect('/')


###not sure where to stick this one, I figure it should be in the same app as locs.

@staff_member_required
def zip_import(request):
    template = 'profiles/import.html'
    try:
        item = ZipData.objects.get(id=1)
        completed = True
        print completed
    except:
        completed = False
        print completed
    if request.method =='POST':
        form = ZipInput(request.POST, request.FILES)
        if form.is_valid():
            records = csv.reader(form.cleaned_data['file'])
            input_data = ZipData()
            ZipData.objects.bulk_create((ZipData(
                                zipcode=line[0],
                                statecode=line[1],
                                lat=line[2],
                                long=line[3],
                                city=line[4],
                                state=line[5]) for line in records), batch_size=500)
            success = True
            context = {
                'completed': completed,
                'form': form,
                'success': success,
            }
            return render_to_response(template, context, context_instance=RequestContext(request))
    else:
        form = ZipInput()
        context = {'form': form,}
        return render_to_response(template, context, context_instance=RequestContext(request))

    
