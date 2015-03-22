from django.shortcuts import render, Http404, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from .models import Order, OrderLineItem, make_conf
from .forms import AddInfoForm
from profiles.models import Location, User, UserProfile
from profiles.forms import CheckAddressForm
from django.views.generic import DetailView
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

from datetime import datetime, timedelta, time

today = datetime.now().date()
tomorrow = today + timedelta(1)
today_start = datetime.combine(today, time())
today_end = datetime.combine(tomorrow, time())
yesterday = (datetime.now() - timedelta(days=1)).date()



def add_info(request,id):
    template = 'orders/add_info.html'
    order = Order.objects.get(id=id)
    location = order.location
    form = AddInfoForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save(commit=False)
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.save()

            return HttpResponseRedirect('/orders/%s/' % order.id)
        
        
    context = {
        'order': order,
        'form': form,
        'location': location,
    }
        
    return render(request, template, context)    
        


### rewrite this to account for anonymous users
#@login_required
def auth_checkout(request, id):
    template = 'orders/checkout.html'
    order = Order.objects.get(id=id)
    request.session['order_id'] = order.id
    line_items = OrderLineItem.objects.filter(order_id=id)
    
    address_form = CheckAddressForm(request.POST or None)
    location = order.location
    ##fill out order details
    order.street_address = request.session['street_address']
    order.zipcode = request.session['zipcode']
    order.city = request.session['city']
    order.state = request.session['state']
    order.save()
    
    if request.user.is_authenticated() == True:
        MyUser = request.user
        print 'MyUser id %s  ' % MyUser.id
        print 'order customer id %s' % order.customer_id
        print 'these two should match'
        if MyUser.id != order.customer_id:
            return Http404
        pub_key = settings.STRIPE_PUBLISHABLE_KEY
        customer_id = request.user.userstripe.stripe_id
        order_total = int(order.total*100)
        if request.method == "POST":
            token = request.POST['stripeToken']
            print request.POST
            try:
                customer = stripe.Customer.retrieve(customer_id)
                customer.cards.create(card=token)
                charge = stripe.Charge.create(
                    amount=order_total, # amount in cents, again
                    currency="usd",
                    customer = customer,
                    description="%s" %(request.user.email)
                )
                order.conf_number = make_conf()
                order.stamped = True
                order.save()
                return HttpResponseRedirect(reverse('orders:order_success', args=[order.id]))
            except stripe.CardError, e:
            # The card has been declined
                raise 'Card has been declined.'
    
    else:
        
        print request.session['anonymous_user_id']
        MyUser_id = request.session['anonymous_user_id']
        MyUser = User.objects.get(id=MyUser_id)
        if MyUser.id != order.customer_id:
            return Http404
        pub_key = settings.STRIPE_PUBLISHABLE_KEY
        order_total = int(order.total*100)
        if request.method == "POST":
            token = request.POST['stripeToken']
            print request.POST
            try:

                charge = stripe.Charge.create(
                    amount=order_total, # amount in cents, again
                    currency="usd",
                    source=token,
                )
                order.conf_number = make_conf()
                order.stamped = True
                order.save()
                return HttpResponseRedirect(reverse('orders:order_success', args=[order.id]))
            except stripe.CardError, e:
            # The card has been declined
                raise 'Card has been declined.'
    
    context = {
        'order': order,
        'line_items': line_items,
        'pub_key': pub_key,
        'location': location,

        'address_form': address_form,
    }
    return render(request, template, context)

def company_home(request):
    template = 'orders/company_home.html'
    MyUser_id = request.user.id
    MyUser = User.objects.get(id=MyUser_id)
    
    context = {
        'MyUser': MyUser,
    }
    
    
    return render(request, template, context)


def order_dashboard(request):
    location = Location.objects.get(id=1)
    template = 'order_dashboard.html'
    MyUser = request.user.userprofile.first_name
    current_orders = Order.objects.filter(created_date__day=today.day).filter(complete=False)
    yesterday_orders = Order.objects.filter(created_date__day=yesterday.day).filter(complete=False)
    outstanding_orders = Order.objects.filter(complete=False)
    if request.user.userprofile.role == 'customer' or None:
        return Http404
    context = {
        'MyUser': MyUser,
        'location': location,
        'current_orders': current_orders,
        'yesterday_orders':yesterday_orders,
        'outstanding_orders': outstanding_orders,
    }
    return render(request, template, context)

def order_status(request):
    context = RequestContext(request)
    order_id = None
    if request.method == 'GET':
        order_id = request.GET['order_id']
        order = Order.objects.get(id=order_id)
        order.complete = True
        order.save()

    return HttpResponse(order.complete)

def order_reverse(request):
    context = RequestContext(request)
    order_id = None
    if request.method == 'GET':
        order_id = request.GET['order_id']
        order = Order.objects.get(id=order_id)
        order.complete = False
        order.save()

    return HttpResponse(order.complete)

class OrderSuccessView(DetailView):
    model = Order
    template_name = 'orders/order_success.html'

    def dispatch(self, *args, **kwargs):
        self.order = Order.objects.get(id=kwargs.get('pk', None))
        return super(OrderSuccessView, self).dispatch(*args, **kwargs)

#
#class single_order_detail(request):
#    if request.method == 'GET':
#        


def receipt_email(request, id):
    order = Order.objects.get(id=id)
    from_email = 'mikesdjangosite@gmail.com'
    to_email = order.customer.email
    conf = order.conf_number
    subject = 'Your order %s' % conf
    line_items = OrderLineItem.objects.filter(order_id=order.id)

    total = '%.2f' % float(order.total)
    
    message_a = '''
    Thank you for your order!\n
    Your confirmation number is %s.\n
    Your items are as follows:\n
    '''% conf
    
    group = []
    
    for line in line_items:
        floated = '%.2f' % float(line.line_price)
        c = '- %s %s: $%s' %(line.size, line, floated)
        group.append(str(c))
    message_b = '\n'.join(group)
    message_c = '\n  Your total is $%s. See you soon!' % total
    
    message = message_a + message_b + '\n' + message_c
    
    send_mail(subject, message, from_email, [to_email])
    
    return HttpResponseRedirect('/')
        
