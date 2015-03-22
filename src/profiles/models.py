import string, random, datetime
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from localflavor.us.models import PhoneNumberField, USStateField, USZipCodeField
from PIL import Image
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


ROLES = (
    ('customer', 'customer'),
    ('employee', 'employee'),
    ('admin', 'admin'),
    ('manager', 'manager'),
)

##get the localflavor addon when making forms.

##modify this to verify against already existing anons

def create_anon_hash(length=30, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(length))


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    role = models.CharField(max_length=120, choices=ROLES, default='customer')
    first_name = models.CharField(max_length=120, blank=True, null=True)
    last_name = models.CharField(max_length=120, blank=True, null=True)
    street_address = models.CharField(max_length=120, blank=True, null=True)
    city = models.CharField(max_length=120, blank=True, null=True)
    state = USStateField(blank=True, null=True)
    zipcode = USZipCodeField(blank=True, null=True)
    phone = PhoneNumberField(blank=True, null=True)
    email = models.EmailField(max_length=120, blank=True, null=True)

    def __unicode__(self):
        return str(self.user)


class UserStripe(models.Model):
    user = models.OneToOneField(User)
    stripe_id = models.CharField(max_length=200, null=True, blank=True)
    
    def __unicode__(self):
    #this will add the username in the stripe_id field
        if self.stripe_id:
            return str(self.stripe_id)
        else:
            return self.user.username


def stripe_callback(sender, request, user, **kwargs):
    user_stripe_account, created = UserStripe.objects.get_or_create(user=user)
    #step one sends back a tuple of whats being created
    if created:
        print "created for %s" % (user.username)
    
    #if the stripe_id for the customer doesnt exist, then make a new stripe id
    #https://stripe.com/docs/api/python#create_customer    
    if user_stripe_account.stripe_id is None or user_stripe_account.stripe_id == '':
        new_stripe_id = stripe.Customer.create(email=user.email)
        user_stripe_account.stripe_id = new_stripe_id['id']
        user_stripe_account.save()

user_logged_in.connect(stripe_callback)


class Location(models.Model):
    street_address = models.CharField(max_length=120)
    city = models.CharField(max_length=120)
    state = USStateField()
    zipcode = USZipCodeField()
    phone = PhoneNumberField()
    email = models.EmailField(max_length=120)
    name = models.CharField(max_length=120)
    monday_open = models.TimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    monday_close = models.TimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    tuesday_open = models.TimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    tuesday_close = models.TimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    wednesday_open = models.TimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    wednesday_close = models.TimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    thursday_open = models.TimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    thursday_close = models.TimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    friday_open = models.TimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    friday_close = models.TimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    saturday_open = models.TimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    saturday_close = models.TimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    sunday_open = models.TimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    sunday_close = models.TimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    message = models.TextField(max_length=1000, blank=True, null=True)
    image = models.ImageField(upload_to='images/%Y/%m/', blank=True, null=True)
    image2 = models.ImageField(upload_to='images/%Y/%m/', blank=True, null=True)
    delivery_radius = models.PositiveIntegerField(default=15)

    ##add in a radius functionality here.
    
    def get_tax_rate(self):
        return Surcharges.objects.filter(location=self.id).latest('timestamp').tax_rate
    
    def get_delivery_charge(self):
        return Surcharges.objects.filter(location=self.id).latest('timestamp').delivery_charge
    
    
    def __unicode__(self):
        return str(self.id)
    
class Surcharges(models.Model):
    location = models.ForeignKey(Location, blank=True, null=True)
    tax_rate = models.DecimalField(max_digits=3, decimal_places=2)
    delivery_charge = models.DecimalField(max_digits=5, decimal_places=2)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    
    def __unicode__(self):
        return str(self.timestamp) + str(self.location.street_address)   
    
class ZipData(models.Model):
    zipcode=models.CharField(max_length=7)
    statecode=models.CharField(max_length=2)
    lat=models.CharField(max_length=120)
    long=models.CharField(max_length=120)
    city=models.CharField(max_length=120)
    state=models.CharField(max_length=120)

    def __unicode__(self):
        return "%s %s %s" %(self.city,self.statecode,self.zipcode)
    
