from django import forms
from .models import Pizza, PizzaTopping, Entree, Side, Product
from orders.models import OrderLineItem, Order



    
class AddPizzaForm(forms.Form):
    product = forms.CharField(max_length=1000, widget=forms.HiddenInput())
    size = forms.CharField(max_length=7, widget=forms.HiddenInput())
    toppings = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple(),required=False, queryset=PizzaTopping.objects.all())
    
 
    
class EditPizzaForm(forms.Form):
    order_line = forms.CharField(max_length=999, widget=forms.HiddenInput())
    toppings = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple(),required=False, queryset=PizzaTopping.objects.all())
    

class AddNoteForm(forms.Form):
    note = forms.CharField(max_length=1000, widget=forms.Textarea(attrs={'cols':30,'rows':8}))
    


class MenuPizzaForm(forms.Form):
    product = forms.CharField(max_length=1000, widget=forms.HiddenInput(), required=False)

    name = forms.CharField(max_length=120)
    description = forms.CharField(max_length=200)
    active = forms.BooleanField(initial=True, required=False)
    small_price = forms.DecimalField(max_digits=20,decimal_places=2)
    medium_price = forms.DecimalField(max_digits=20,decimal_places=2)
    large_price = forms.DecimalField(max_digits=20,decimal_places=2)
    xl_price = forms.DecimalField(max_digits=20,decimal_places=2)
    jumbo_price = forms.DecimalField(max_digits=20,decimal_places=2)
    
        
class MenuEntreeForm(forms.Form):
    product = forms.CharField(max_length=1000, widget=forms.HiddenInput(), required=False)

    name = forms.CharField(max_length=120)
    description = forms.CharField(max_length=200)
    active = forms.BooleanField(initial=True, required=False)
    small_price = forms.DecimalField(max_digits=20,decimal_places=2)
    large_price = forms.DecimalField(max_digits=20,decimal_places=2)



        
class MenuSideForm(forms.Form):
    product = forms.CharField(max_length=1000, widget=forms.HiddenInput(), required=False)

    name = forms.CharField(max_length=120)
    description = forms.CharField(max_length=200)
    active = forms.BooleanField(initial=True, required=False)
    price = forms.DecimalField(max_digits=20,decimal_places=2)
    


        
     
