from django.shortcuts import render, HttpResponseRedirect, Http404, RequestContext, HttpResponse
from django.contrib import messages
from .models import Pizza, PizzaTopping, Product, Entree, Side
from profiles.models import UserProfile, User, Location, create_anon_hash
from profiles.forms import CheckAddressForm
from .forms import AddPizzaForm, EditPizzaForm, AddNoteForm, MenuEntreeForm, MenuPizzaForm, MenuSideForm
from orders.models import Order, OrderLineItem
from profiles.radiuscheck import calc_dist_fixed
import json
from menu.menu_helpers import ordermaker
from django.views.generic import ListView

# Create your views here.




def menu_home(request):
    template = 'menu/menu_home.html'
    specialties = Product.objects.filter(product_type='P').all()
    breadsticks = Product.objects.filter(product_type='B').all()

    wings = Product.objects.filter(product_type='W').all()
    salads = Product.objects.filter(product_type='D').all()
    soups = Product.objects.filter(product_type='O').all()
    sandwiches = Product.objects.filter(product_type='H').all()
    beverages = Product.objects.filter(product_type='B').all()
    pasta_dishes = Product.objects.filter(product_type='T').all()
    sides = Product.objects.filter(product_type='S').all()
    toppings_available = PizzaTopping.objects.filter(active=True) 
    products = Product.objects.all()
    address_form = CheckAddressForm(request.POST or None)
    add_pizza_form = AddPizzaForm(request.POST or None)
    edit_pizza_form = EditPizzaForm(request.POST or None)
    add_note_form = AddNoteForm(request.POST or None)
    
    #1. check if authenticated.
    if request.user.is_authenticated() == True:
        print 'user authenticated'
        #make an auth user variable to work with.
        MyUser = request.user
        #1a:1.if authenticated and not overridden for address, get most recent address info.
        #READ THE EXCEPT CLAUSE FIRST!
        try:
            
            request.session['delivery_override']
            override = request.session['delivery_override']
            #if overridden, replace old address info with new info.
            #we need to use session data, because an order might not
            #have been created yet.
            street_address = request.session['street_address']
            zipcode = request.session['zipcode']
            city = request.session['city']
            state = request.session['state']
            #do the same for delivery status and for session location, and for address_check.
            location_id = request.session['location']
            print location_id
            location = Location.objects.get(id=location_id)
            delivery_available = request.session['delivery_available']
            address_checked = True
            print 'try 1a complete'
            ## the order status will be done
            
        
        #1a:2 if not overridden, go ahead with placing in old information.
        except:
            print 'exception 1a'
            #filter by created date for time being, add a field in Order for #recvd date.
            try:
                mem_id = Order.objects.filter(customer_id=MyUser.id).latest('created_date').id
                recent = Order.objects.get(id=mem_id)
                # no need for session variables just yet. we can feed them directly to the view.
                
                street_address = recent.street_address
                print street_address
                zipcode = recent.zipcode
                city = recent.city
                state = recent.state
                #set the session location to the most recent delivery address.
                location = recent.location
                request.session['street_address'] = street_address
                print request.session['street_address']
                request.session['zipcode'] = zipcode
                request.session['city'] = city
                request.session['state'] = state
                request.session['location'] = location.id
                #set current delivery avail to recent.set 'address checked' to true, since that
                #was done last time.
                delivery_available = recent.delivery_available
                print delivery_available
                request.session['delivery_available'] = delivery_available
                address_checked = True
                request.session['address_checked'] = address_checked
            #for the case when a new user is made without a prior order
            except:
                #check if address checked
                try:
                    request.session['delivery_override']
                    print 'a'
                    address_checked = True
                    delivery_available = request.session['delivery_available']
                    print 'b'
                    street_address = request.session['street_address']
                    print 'c'
                    zipcode = request.session['zipcode']
                    city = request.session['city']
                    state = request.session['state']
                    print 'd'
                    location_id = request.session['location']
                    print location
                    location = Location.objects.get(id=location_id)
                except:    
                    
                    address_checked = False
                    delivery_available = False
                    street_address = False
                    zipcode = False
                    city = False
                    state = False
                    location = Location.objects.get(id=1)
            #dont create an order until a line item has been added.
        #1b:1. after establishing order parameters, determine if an order exists,
        #so what we can populate the sidebar. Orders should only be created once
        #items are added. the existence of a user does not mean an order exists.
        try:
            #the existence of order id in session will correspond withh an order.
            request.session['order_id']
            order_id = request.session['order_id']
            # grab the order and its line items
            order = Order.objects.get(id=order_id)
            order.first_name = MyUser.userprofile.first_name
            print order.first_name
            order.last_name = MyUser.userprofile.last_name
            order.phone = MyUser.userprofile.phone
            print order.phone
            order.save()
            line_items = order.orderlineitem_set.all()
            print 'try 1b complete'
        
        #if the order doesn't exist, simply pass None to the view.
        except:
            order = False
            line_items = None
            print 'exception 1b caught'
        
    #2.anonymous users.
    elif request.user.is_authenticated() == False:
        #first, check if there's already an anonymous user in session
        try:
            #if so, pass the anon user to MyUser
            request.session['anonymous_user_id']
            anonymous_user_id = request.session['anonymous_user_id']
            MyUser = User.objects.get(id=anonymous_user_id)
        except:
            #with no anonymous user, user a randomizer and make one.
            username = create_anon_hash()
            anonymous_user, created = User.objects.get_or_create(username=username)
            request.session['anonymous_user_id'] = anonymous_user.id
            MyUser = User.objects.get(id=anonymous_user.id)
        #next, check if the session has a location specified.We shouldnt combine
        #this with order checking - remember that an order is created at adding.
        try:
            request.session['location']
            # we need to query locations based on the session, unlike the anon user.
            location_id = request.session['location']
            location = Location.objects.get(id=location_id)
        except:
            #with no existing location, default to home office.
            location = Location.objects.get(id=1)
        
        #check to see if delivery is available. 
        try:
            request.session['address_checked']
            #set the variable to pass to the view equal to the result of address check
            address_checked = request.session['address_checked']
            ##the results of address check will determine availability
            delivery_available = request.session['delivery_available']
            ## use the affirmative results to pass the info to the view
            street_address = request.session['street_address']
            city = request.session['city']
            state = request.session['state']
            zipcode = request.session['zipcode']
            
        except:
            address_checked = False
            delivery_available = False
            street_address = False
            city = False
            state = False
            zipcode = False
            
        #last, check the existence of an order 
        try:
            request.session['order_id']
            order_id = request.session['order_id']
            order = Order.objects.get(id=order_id)
            print 'order ## last'
            line_items = order.orderlineitem_set.all()
            if delivery_available == True:
                order.delivery_available = True
                order.save()
            else:
                order.delivery_available = False
                order.save()
        except:
            order = False
            print 'order false'
            line_items = None
    try:
        order.id
        print 'order id %s' % order.id
    except:
        print 'no order id'


    context = {
        'specialties': specialties,
        'breadsticks': breadsticks,
        'wings':wings,
        'salads':salads,
        'soups':soups,
        'sandwiches':sandwiches,
        'beverages':beverages,
        'pasta_dishes':pasta_dishes,
        'sides':sides,
        'toppings_available':toppings_available,
        'products':products,
        'address_form':address_form,
        'add_pizza_form':add_pizza_form,
        'edit_pizza_form':edit_pizza_form,
        'add_note_form': add_note_form,
        'street_address':street_address,
        'zipcode':zipcode,
        'city':city,
        'state':state,
        'delivery_available':delivery_available,
        'address_checked':address_checked,
        'MyUser': MyUser,
        'order':order,
        'line_items':line_items,
        'location':location,
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
            print form.cleaned_data['street_address']
            zipcode = form.cleaned_data['zipcode']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            request.session['street_address'] = street_address
            request.session['zipcode'] = zipcode
            request.session['city'] = city
            request.session['state'] = state
            
            result = calc_dist_fixed(zipcode)
            request.session['location'] = Location.objects.get(id=result[1]).id
            request.session['address_checked'] = True
            print result[0]
            print result[1]
            if result[0] == True:
                request.session['delivery_available'] = True
                request.session['delivery_override'] = True
                print request.session['location']
                
            elif result[0] == False:
                request.session['delivery_available'] = False
                request.session['delivery_override'] = True
                print request.session['location']
            return HttpResponseRedirect('/menu/')
             
        return HttpResponseRedirect('/menu/')
    
    else:
        return Http404

      

def change_address(request):
    if request.method == 'POST':
        
        # make the address validator script loop through a couple locations.
        form = CheckAddressForm(request.POST or None)
    
        if form.is_valid():
            form.save(commit=False)
            street_address = form.cleaned_data['street_address']
            print type(street_address)
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
                
                
            try:
                order_id = request.session['order_id']
                order = Order.objects.get(id=order_id)
                loc_id = request.session['location']
                order.location = Location.objects.get(id=loc_id)
                order.save()
                order.subtotal = order.compute_subtotal()
                order.taxes = order.compute_taxes()
                order.total = order.compute_total()
                order.save()
            except:
                print 'no order on file yet'
                pass
            
            return HttpResponseRedirect('/menu/')
             
        return HttpResponseRedirect('/menu/')
    
    else:
        return Http404






def add_pizza(request):
    order = ordermaker(request)
        
    
    ###this is the juncture point as to when it becomes a pizza vs other.
    if request.method == 'POST':
        form = AddPizzaForm(request.POST or None)
        
        if form.is_valid():
            product_id = form.cleaned_data['product']
            size = form.cleaned_data['size']
            pizza = Pizza.objects.get(id=product_id, size=size)
            line_price = []
            line_price.append(pizza.get_price())
            #we can either feed a 'none' to toppings at instantiation
            #or we can just repurpose toppings to mean other stuff.
            #it's likely best if we modify the original 'toppings'
            #that was designed for the cheese pizza to be 'extra toppings'
            #and we really only count 'extra toppings (aka 'extras') towards
            #the final price.
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


def add_entree(request, id):
    order = ordermaker(request)              
    

    entree = Entree.objects.get(id=id)
    
    line_item = OrderLineItem.objects.create(
                            order_id=order.id,
                            product_id=entree.product_id,
                            line_price=entree.get_price(),
                            product_type=entree.product.product_type,
                            size=entree.size,
                            )
            

    line_item.save()
    order.subtotal = order.compute_subtotal()
    order.taxes = order.compute_taxes()
    order.total = order.compute_total()
    order.save()

            
    return HttpResponseRedirect('/menu/')


##break this out into the item types with and without toppings.
# we really dont need the edit line item visible for non pizza.
def edit_line_item(request):
    order_id = request.session['order_id']
    order = Order.objects.get(id=order_id)
    
    
    if request.method == 'POST':
        form = EditPizzaForm(request.POST or None)
        
        if form.is_valid():

            line_item_id = form.cleaned_data['order_line']
            line_item = OrderLineItem.objects.get(id=line_item_id)
            #we can either feed a 'none' to toppings at instantiation
            #or we can just repurpose toppings to mean other stuff.
            #it's likely best if we modify the original 'toppings'
            #that was designed for the cheese pizza to be 'extra toppings'
            #and we really only count 'extra toppings (aka 'extras') towards
            #the final price.
            line_item.toppings = []
            toppings = form.cleaned_data['toppings']
            new_line_price = []
            
            for i in toppings:
                line_item.toppings.add(i)
            new_line_price.append(line_item.get_price())
            line_item.line_price = sum(new_line_price)
            
            line_item.save()

            order.subtotal = order.compute_subtotal()
            order.taxes = order.compute_taxes()
            order.total = order.compute_total()
            order.save()
            
                 
        else:
            print form.errors
        
    return HttpResponseRedirect('/menu/')



def add_note(request):
    order_id = request.session['order_id']
    order = Order.objects.get(id=order_id)
    
    if request.method == 'POST':
        form = AddNoteForm(request.POST or None)
        if form.is_valid():
            order.note = form.cleaned_data['note']
            order.save()
        
        else:
            print form.errors
            
    return HttpResponseRedirect('/menu/')


def set_pickup(request):
    if request.method == 'GET':
        order_id = request.session['order_id']
        order = Order.objects.get(id=order_id)
        order.delivery = False
        order.subtotal = order.compute_subtotal()
        order.taxes = order.compute_taxes()
        order.total = order.compute_total()
        order.save()
        subtotal = str(order.compute_subtotal())
        taxes = str(order.compute_taxes())
        total = str(order.compute_total())
        
        data = json.dumps({
            'subtotal': subtotal,
            'taxes':taxes,
            'total':total,
        })
        return HttpResponse(data, content_type='application/json')





def set_delivery(request):
    if request.method == 'GET':
        order_id = request.session['order_id']
        order = Order.objects.get(id=order_id)
        order.delivery = True
        order.subtotal = order.compute_subtotal()
        order.taxes = order.compute_taxes()
        order.total = order.compute_total()
        order.save()
        delivery_charge = str(order.get_delivery_charge())
        subtotal = str(order.compute_subtotal())
        taxes = str(order.compute_taxes())
        total = str(order.compute_total())
        
        data = json.dumps({
            'delivery_charge':delivery_charge,
            'subtotal':subtotal,
            'taxes':taxes,
            'total':total,
        })
        return HttpResponse(data, content_type='application/json')


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


    

    
    
def menu_group(request,exp):
    object_list = Product.objects.filter(product_type=exp)
    template = 'menu/menu_group.html'
    exp = exp
    if exp == 'P':
        form = MenuPizzaForm
    elif exp == 'S' or exp == 'G':
        form = MenuSideForm
    else:
        form = MenuEntreeForm
    
    
    context = {
        'object_list':object_list,
        'form':form,
        'exp':exp,
    }
    
    return render(request, template, context)

    product = forms.CharField(max_length=1000, widget=forms.HiddenInput())
#do product type at view level
    name = forms.CharField(max_length=120)
    description = forms.CharField(max_length=200)
    active = forms.BooleanField()
    small_price = forms.DecimalField(max_digits=20,decimal_places=2)
    medium_price = forms.DecimalField(max_digits=20,decimal_places=2)
    large_price = forms.DecimalField(max_digits=20,decimal_places=2)
    xl_price = forms.DecimalField(max_digits=20,decimal_places=2)
    jumbo_price = forms.DecimalField(max_digits=20,decimal_places=2)





def edit_product(request, exp):
    print exp
    if exp == 'P':
        print 'a'
        if request.method == 'POST':
            print 'b'
            form = MenuPizzaForm(request.POST or None)
            if form.is_valid():
                print 'c'
                print form.cleaned_data['product']
                product = Product.objects.get(id=form.cleaned_data['product'])
                product.description = form.cleaned_data['description']
                product.active = form.cleaned_data['active']
                product.small_price = form.cleaned_data['small_price']
                product.medium_price = form.cleaned_data['medium_price']
                product.large_price = form.cleaned_data['large_price']
                product.xl_price = form.cleaned_data['xl_price']
                product.jumbo_price = form.cleaned_data['jumbo_price']
                product.save()

        
            return HttpResponseRedirect('/menu/%s' %exp)
                
    elif exp == 'S' or exp == 'G':

        if request.method == 'POST':

            form = MenuSideForm(request.POST or None)
            if form.is_valid():

                product = Product.objects.get(id=form.cleaned_data['product'])
                product.description = form.cleaned_data['description']
                product.active = form.cleaned_data['active']
                product.large_price = form.cleaned_data['price']
                product.save()
            return HttpResponseRedirect('/menu/%s' %exp)
    else:
        if request.method == 'POST':
            form = MenuEntreeForm(request.POST or None)
            if form.is_valid():
                product = Product.objects.get(id=form.cleaned_data['product'])
                product.description = form.cleaned_data['description']
                product.active = form.cleaned_data['active']
                product.small_price = form.cleaned_data['small_price']
                product.large_price = form.cleaned_data['large_price']
                product.save()
            return HttpResponseRedirect('/menu/%s' %exp)        

        
        
def create_product(request, exp):
    print exp
    if exp == 'P':
        if request.method == 'POST':
            form = MenuPizzaForm(request.POST or None)
            if form.is_valid():
                print form.cleaned_data['product']
                print form.cleaned_data['name']
                print form.cleaned_data['description']
                print form.cleaned_data['active']
                print form.cleaned_data['small_price']
                print form.cleaned_data['medium_price']
                print form.cleaned_data['large_price']
                print form.cleaned_data['xl_price']
                print form.cleaned_data['jumbo_price']
                product = Product.objects.create(
                    name=form.cleaned_data['name'],
                    product_type='P',
                    description=form.cleaned_data['description'],
                    active=form.cleaned_data['active'],
                    small_price=form.cleaned_data['small_price'],
                    medium_price=form.cleaned_data['medium_price'],
                    large_price=form.cleaned_data['large_price'],
                    xl_price=form.cleaned_data['xl_price'],
                    jumbo_price=form.cleaned_data['jumbo_price'],
                )
                small = Pizza.objects.create(
                    product=product,
                    size='SMALL',
                )
                medium = Pizza.objects.create(
                    product=product,
                    size='MEDIUM',
                )
                large = Pizza.objects.create(
                    product=product,
                    size='LARGE',
                )
                xl = Pizza.objects.create(
                    product=product,
                    size='XL',
                )
                jumbo = Pizza.objects.create(
                    product=product,
                    size='JUMBO',
                )
                print '5 pizzas created'
                
                
                
                
            return HttpResponseRedirect('/menu/%s' %exp)
    elif exp == 'S' or exp == 'G':
        if request.method == 'POST':
            form = MenuSideForm(request.POST or None)
            if form.is_valid():
                if exp == 'S':
                    product = Product.objects.create(
                        name=form.cleaned_data['name'],
                        product_type='S',
                        description=form.cleaned_data['description'],
                        active=form.cleaned_data['active'],
                        large_price=form.cleaned_data['price'],
                    )
                    Side.objects.create(
                        product=product,
                        name=form.cleaned_data['name'],
                        description=form.cleaned_data['description'],
                        active=form.cleaned_data['active'],
                        price=form.cleaned_data['price']
                    )
                else:
                    product = Product.objects.create(
                        name=form.cleaned_data['name'],
                        product_type='S',
                        description=form.cleaned_data['description'],
                        active=form.cleaned_data['active'],
                        large_price=form.cleaned_data['price'],
                    )
                    PizzaTopping.objects.create(
                        product=product,
                        name=form.cleaned_data['name'],
                        description=form.cleaned_data['description'],
                        active=form.cleaned_data['active'],
                        price=form.cleaned_data['price']
                    )

            return HttpResponseRedirect('/menu/%s' %exp)
    else:
        if request.method == 'POST':
            form = MenuEntreeForm(request.POST or None)
            if form.is_valid():
                product = Product.objects.create(
                    name=form.cleaned_data['name'],
                    product_type=exp,
                    description=form.cleaned_data['description'],
                    active=form.cleaned_data['active'],
                    small_price=form.cleaned_data['small_price'],
                    large_price=form.cleaned_data['large_price'],
                )
                small = Entree.objects.create(
                    product=product,
                    size='SMALL',
                )
                large = Entree.objects.create(
                    product=product,
                    size='LARGE',
                )

            return HttpResponseRedirect('/menu/%s' %exp)      
        
        
        