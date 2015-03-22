from django import forms
from .models import Order
from localflavor.us.forms import USZipCodeField, USStateField, USPhoneNumberField


## client facing
class AddInfoForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone']
    
    
#### employee facing.    
    
    
