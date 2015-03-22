from django.db import models

# Create your models here.
from decimal import Decimal


##get rid of side!
class Product(models.Model):
    PIZZA = 'P'
    SIDE = 'S'
    SOUP = 'O'
    SALAD = 'D'
    BREADSTICKS = 'B'
    PASTA = 'T'
    WINGS = 'W'
    SANDWICH = 'H'
    BEVERAGE = 'E'
    TOPPING = 'G'
    ITEM_TYPES = (

        (PIZZA, 'PIZZA'),
        (SIDE, 'SIDE'),
        (SOUP,'SOUP'),
        (SALAD,'SALAD'),
        (BREADSTICKS,'BREADSTICKS'),
        (PASTA,'PASTA'),
        (WINGS,'WINGS'),
        (SANDWICH,'SANDWICH'),
        (BEVERAGE,'BEVERAGE'),
        (TOPPING, 'TOPPING'),
    )
    product_type = models.CharField(max_length=50, choices=ITEM_TYPES, default=PIZZA)
    name = models.CharField(max_length=120)
    description = models.CharField(max_length=200)
    active = models.BooleanField(default=True)
    small_price = models.DecimalField(max_digits=20, decimal_places=2, default=None, blank=True, null=True)
    medium_price = models.DecimalField(max_digits=20, decimal_places=2, default=None, blank=True, null=True)
    large_price = models.DecimalField(max_digits=20, decimal_places=2, default=None)
    xl_price = models.DecimalField(max_digits=20, decimal_places=2, default=None, blank=True, null=True)
    jumbo_price = models.DecimalField(max_digits=20, decimal_places=2, default=None, blank=True, null=True)
    
    ##make this so that it works through the different item types
    
    def get_small(self):
        if self.product_type == 'PIZZA':
            return Pizza.objects.filter(product=self.id).get(size='SMALL')
        else:
            return Entree.objects.filter(product=self.id).get(size='SMALL')
    
    def get_medium(self):
        return Pizza.objects.filter(product=self.id).get(size='MEDIUM')
    
    def get_large(self):
        if self.product_type == 'PIZZA':
            return Pizza.objects.filter(product=self.id).get(size='LARGE')
        else:
            return Entree.objects.filter(product=self.id).get(size='LARGE')
    
    def get_xl(self):
        return Pizza.objects.filter(product=self.id).get(size='XL')
    
    def get_jumbo(self):
        return Pizza.objects.filter(product=self.id).get(size='JUMBO')
    
        
    
    def __unicode__(self):
        return self.name
    
    
class PizzaTopping(models.Model):
    product = models.ForeignKey(Product, blank=True, null=True)
    name = models.CharField(max_length=120)
    description = models.CharField(max_length=200)
    active = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=20, decimal_places=2, default=None)
    
    def get_product_name(self):
        return self.product.name
    
    def get_product_description(self):
        return self.product.description
    
    def get_price(self):
            return self.product.large_price

    def __unicode__(self):
        return self.name
    

    
class Pizza(models.Model):
    product = models.ForeignKey(Product)
    toppings = models.ManyToManyField(PizzaTopping, blank=True, null=True)
    SMALL = 'SMALL'
    MEDIUM = 'MEDIUM'
    LARGE = 'LARGE'
    XL = 'XL'
    JUMBO = 'JUMBO'
    SIZE_CHOICES = (
        (SMALL, 'SMALL'),
        (MEDIUM, 'MEDIUM'),
        (LARGE, 'LARGE'),
        (XL, 'XL'),
        (JUMBO, 'JUMBO'),
    )
    size = models.CharField(max_length=7, choices=SIZE_CHOICES, default=LARGE)

    specialty = models.BooleanField(default=True)
    
    def get_product_name(self):
        return self.product.name
    
    def get_product_description(self):
        return self.product.description
    
    def get_price(self):
        if self.size == 'SMALL':
            return self.product.small_price
            
        elif self.size == 'MEDIUM':
            return self.product.medium_price
            
        elif self.size == 'LARGE':    
            return self.product.large_price
            
        elif self.size == 'XL':
            return self.product.xl_price
    
        elif self.size == 'JUMBO':
            return self.product.jumbo_price
    
    class Meta:
        unique_together = (('product', 'size'))
    
    def __unicode__(self):
        return '%s %s' % (self.size, self.product)
    
class Entree(models.Model):
    product = models.ForeignKey(Product)
    SMALL = 'SMALL'
    LARGE = 'LARGE'
    SIZE_CHOICES = (
        (SMALL,'SMALL'),
        (LARGE,'LARGE'),
    )
    size = models.CharField(max_length=7, choices=SIZE_CHOICES, default=LARGE)

    
    def get_name(self):
        return self.product.name
    
    def get_product_description(self):
        return self.product.description
    
    def get_price(self):
        if self.size == 'SMALL':
            return self.product.small_price
        elif self.size == 'LARGE':
            return self.product.large_price
            
    class Meta:
        unique_together = (('product','size'))
        
    def __unicode__(self):
        return '%s %s' %(self.size, self.product)
    
   
class Side(models.Model):
    product = models.ForeignKey(Product, blank=True, null=True)
    name = models.CharField(max_length=120)
    description = models.CharField(max_length=200)
    active = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=20, decimal_places=2, default=None)

    def __unicode__(self):
        return self.name
    

