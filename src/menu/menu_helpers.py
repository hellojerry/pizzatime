from django.shortcuts import render, HttpResponseRedirect, Http404, RequestContext, HttpResponse
from django.contrib import messages
from .models import Pizza, PizzaTopping, Product, Entree, Side
from profiles.models import UserProfile, User, Location, create_anon_hash
from profiles.forms import CheckAddressForm
from .forms import AddPizzaForm, EditPizzaForm, AddNoteForm
from orders.models import Order, OrderLineItem
from profiles.radiuscheck import calc_dist_fixed
import json





#we can move this big if else chunk out to a separate function,
#since we'll be doing the exact same thing three times for pizza,
#entrees/appetizers, and beverages.

def ordermaker(request):
    location = request.session['location']

    if request.user.is_authenticated():
        customer_id = request.user.id
        print 'customer id %s' % customer_id
        try:
            order_id = request.session['order_id']
            print 'order id %s instantiated at line 221' % order_id
        except:
            order_id = False
        try:
            order = Order.objects.get(id=order_id)
            print 'order'
        except Order.DoesNotExist:
            order = Order.objects.create(customer_id=customer_id, location_id=location)
            print order.customer.id
            print 'created %s' % order.id
            if request.session['delivery_available'] == True:
                order.delivery_available = True
                order.street_address = request.session['street_address']
                order.city = request.session['city']
                order.state = request.session['state']
                order.zipcode = request.session['zipcode']
                order.save()
                print 'delivery avail on model is %s' % order.delivery_available
                request.session['order_id'] = order.id
            else:
                order.delivery_available = False
                order.street_address = request.session['street_address']
                order.city = request.session['city']
                order.state = request.session['state']
                order.zipcode = request.session['street_address']
                order.save()
                print order.delivery_available
                print 'delivery avail on model is %s' % order.delivery_available
                request.session['order_id'] = order.id
    
    else:
        print 'else clause'
        try:
            order_id = request.session['order_id']
        except:
            order_id = False
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            anonymous_user = User.objects.get(id=request.session['anonymous_user_id'])
            order = Order(customer_id=anonymous_user.id, location_id=location)
            if request.session['delivery_available'] == True:
                order.delivery_available = True
                order.save()
                #print 'delivery avail on model is %s' % delivery_available
                request.session['order_id'] = order.id
            else:
                order.delivery_available = False
                order.save()
                #print 'delivery avail on model is %s' % delivery_available
                request.session['order_id'] = order.id
    return order