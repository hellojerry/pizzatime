from django.shortcuts import render, HttpResponseRedirect, Http404, RequestContext
from django.contrib import messages
from .models import Pizza, PizzaTopping, Product
from profiles.models import UserProfile, User, Location
from profiles.forms import CheckAddressForm
from .forms import AddPizzaForm, EditPizzaForm
from orders.models import Order, OrderLineItem
from profiles.radiuscheck import calc_dist_fixed
# Create your views here.


#rewrite this


def menu_home(request):
    template = 'menu/menu_home.html'
    specialties = Product.objects.filter(product_type='PIZZA').all()
    toppings_available = PizzaTopping.objects.filter(active=True) 
    products = Product.objects.all()
    address_form = CheckAddressForm(request.POST or None)
    add_pizza_form = AddPizzaForm(request.POST or None)
    edit_pizza_form = EditPizzaForm(request.POST or None)
    
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
    
    

    try:
        request.session['order_id']
        order_id = request.session['order_id']
        print order_id
        order = Order.objects.get(id=order_id)
        line_items = order.orderlineitem_set.all()
    except:
        order = False
        print 'no order id'
        line_items = None
        
    try:
        request.session['delivery_available']
        print 'request detected'
        if request.session['delivery_available'] == True:
            delivery_avail = True
            address_checked = True
            print 'deliv available'
        else:
            delivery_avail = False
            address_checked = True
            print 'deliv avail set to false'
    except:
        delivery_avail = False
        address_checked = False
        request.session['delivery_available'] = False
        print 'deliv avail set to false in except stamt line 62'
    
    try:
        request.session['street_address']
        request.session['zipcode']
        request.session['city']
        request.session['state']
        street_address = request.session['street_address']
        zipcode = request.session['zipcode']
        city = request.session['city']
        state = request.session['state']
    except:
        street_address = False
        zipcode = False
        city = False
        state = False
    
    
    if request.user.is_authenticated() == True:
        print 'hello'
        MyUser = request.user
        mem_id = Order.objects.filter(customer_id=MyUser.id).latest('created_date').id
        print mem_id
        print 'customer id'
        recent = Order.objects.get(id=mem_id)
        request.session['street_address'] = recent.street_address
        request.session['zipcode'] = recent.zipcode
        request.session['city'] = recent.city
        request.session['state'] = recent.state
        street_address = request.session['street_address']
        zipcode = request.session['zipcode']
        city = request.session['city']
        state = request.session['state']
        print recent.delivery_avail
        print 'before if clause'
        if recent.delivery_avail == True:
            request.session['delivery_available'] = True
            delivery_avail = request.session['delivery_available']
            address_checked = True
            'print address_checked'
            try:
                request.session['delivery_override']
                delivery_avail = request.session['delivery_override']
                print delivery_avail
        else:
            request.session['delivery_available'] = False
            delivery_avail = request.session['delivery_available']
            address_checked = True
            print 'address checked %s' % address_checked
        print 'auth user'
        
    elif request.user.is_authenticated() == False:
        raw_username = str(request.COOKIES['sessionid'])
        username = raw_username
        if len(raw_username) > 30:
            username = raw_username[:30]
        anonymous_user, created = User.objects.get_or_create(username=username)
        request.session['anony_id'] = anonymous_user.id
        MyUser = request.session['anony_id']
        try:
            order_id = request.session['order_id']
            print 'order id %s' % order_id
        except:
            order_id = False
        try:
            order = Order.objects.get(id=order_id)
            if request.session['delivery_available'] == True:
                order.delivery_avail = True
                order.save()
                print 'delivery avail %s' % order.delivery_avail
            elif request.session['delivery_available'] == False:
                order.delivery_avail = False
                order.save()
                print 'delivery avail %s' % order.delivery_avail
        except Order.DoesNotExist:
            order = Order(customer_id=anonymous_user.id, location=location)
            order.save()
            print 'order instantiated line 119'
            request.session['order_id'] = order.id
    
    context = {
        'address_form': address_form,
        'add_pizza_form': add_pizza_form,
        'edit_pizza_form': edit_pizza_form,
        'products': products,
        'specialties': specialties,
        'toppings_available': toppings_available,
        'MyUser': MyUser,
        'order': order,
        'line_items': line_items,
        'location': location,
        'delivery_avail':delivery_avail,
        'address_checked':address_checked,
        'street_address':street_address,
        'zipcode':zipcode,
        'city':city,
        'state':state,
    }
    
    return render(request, template, context)




##we're going to replace this function wish an ajax form submission.

def check_address(request):
    if request.method == 'POST':
        
        # make the address validator script loop through a couple locations.
        form = CheckAddressForm(request.POST or None)
    
        if form.is_valid():
            form.save(commit=False)
            street_address = form.cleaned_data['street_address']
            zipcode = form.cleaned_data['zipcode']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            request.session['street_address'] = street_address
            request.session['zipcode'] = zipcode
            request.session['city'] = city
            request.session['state'] = state
            
            result = calc_dist_fixed(zipcode)
            request.session['location'] = Location.objects.get(id=result[1]).id
            
            print result[0]
            print result[1]
            if result[0] == True:
                request.session['delivery_available'] = True
                print request.session['location']
                
            elif result[0] == False:
                request.session['delivery_available'] = False
                print request.session['location']
            return HttpResponseRedirect('/menu/')
             
        return HttpResponseRedirect('/menu/')
    
    else:
        return Http404

#def use_last_address(request):
#    if request.method == 'POST':
        
def use_last_address(request):
    context = RequestContext(request)
    user_id = request.user.id
    if request.method == 'GET':
        last_order_id = Order.objects.filter(customer_id=user_id).latest('created_at').id
        last_order = Order.objects.get(id=last_order_id)
        request.cont
        
        order_id = request.GET['order_id']
        
        order = Order.objects.get(id=order_id)
        order.complete = False
        order.save()

    return HttpResponse(order.complete)        

def change_address(request):
    if request.method == 'POST':
        
        # make the address validator script loop through a couple locations.
        form = CheckAddressForm(request.POST or None)
    
        if form.is_valid():
            form.save(commit=False)
            street_address = form.cleaned_data['street_address']
            zipcode = form.cleaned_data['zipcode']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            request.session['street_address'] = street_address
            request.session['zipcode'] = zipcode
            request.session['city'] = city
            request.session['state'] = state
            
            result = calc_dist_fixed(zipcode)
            request.session['location'] = Location.objects.get(id=result[1]).id
            #.id
            
            
            if result[0] == True:
                request.session['delivery_available'] = True
                request.session['delivery_override'] = True
                
            elif result[0] == False:
                request.session['delivery_available'] = False
                request.session['delivery_override'] = False
                print request.session['location']
                
            try:
                order_id = request.session['order_id']
                order = Order.objects.get(id=order_id)
                order.location = request.session['location']
                order.save()
            except:
                print 'no order on file yet'
                pass
            
            return HttpResponseRedirect('/menu/')
             
        return HttpResponseRedirect('/menu/')
    
    else:
        return Http404






def add_pizza(request):
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
                order.delivery_avail = True
                order.save()
                print 'delivery avail on model is %s' % delivery_avail
                request.session['order_id'] = order.id
            else:
                order.delivery_avail = False
                order.save()
                print order.delivery_avail
                print 'delivery avail on model is %s' % delivery_avail
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
            order = Order(customer_id=anonymous_user.id, location_id=location)
            if request.session['delivery_available'] == True:
                order.delivery_avail = True
                order.save()
                print 'delivery avail on model is %s' % delivery_avail
                request.session['order_id'] = order.id
            else:
                order.delivery_avail = False
                order.save()
                print 'delivery avail on model is %s' % delivery_avail
                request.session['order_id'] = order.id
        
    ##we ne
    
    if request.method == 'POST':
        form = AddPizzaForm(request.POST or None)
        
        if form.is_valid():
            product_id = form.cleaned_data['product']
            size = form.cleaned_data['size']
            pizza = Pizza.objects.get(id=product_id, size=size)
            line_price = []
            line_price.append(pizza.get_price())
            toppings = form.cleaned_data['toppings']

            for i in toppings:
                line_price.append(i.price)
                
            line_item = OrderLineItem.objects.create(
                order_id=order.id, product_id=pizza.product_id,
                line_price=sum(line_price), size=size)
            
            line_item.save()
            for i in toppings:
                line_item.toppings.add(i)
            line_item.save()
            order.subtotal = order.compute_subtotal()
            order.taxes = order.compute_taxes()
            order.total = order.compute_total()
            order.save()
                
        else:
            print form.errors
        
    return HttpResponseRedirect('/menu/')

def edit_line_item(request):
    order_id = request.session['order_id']
    order = Order.objects.get(id=order_id)
    
    
    if request.method == 'POST':
        form = EditPizzaForm(request.POST or None)
        
        if form.is_valid():

            line_item_id = form.cleaned_data['order_line']
            line_item = OrderLineItem.objects.get(id=line_item_id)

            toppings = form.cleaned_data['toppings']
            new_line_price = []
            new_line_price.append(line_item.get_price())
            for i in toppings:
                new_line_price.append(i.price)

            line_item.line_price = sum(new_line_price)
            line_item.toppings = []
            line_item.save()

            for i in toppings:
                line_item.toppings.add(i)

            line_item.save()
            order.subtotal = order.compute_subtotal()
            order.taxes = order.compute_taxes()
            order.total = order.compute_total()
            order.save()
            
                
                
        else:
            print form.errors
        
    return HttpResponseRedirect('/menu/')

def edit_order(request):
    order_id = request.session['order_id']
    order = Order.objects.get(id=order_id)
    
    


def delete_line_item(request, id):
    order_id = request.session['order_id']
    order = Order.objects.get(id=order_id)
    line_item = OrderLineItem.objects.get(id=id)
    line_item.delete()
    order.subtotal = order.compute_subtotal()
    order.taxes = order.compute_taxes()
    order.total = order.compute_total()
    order.save()

    return HttpResponseRedirect('/menu/')
