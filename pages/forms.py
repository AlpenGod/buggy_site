from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.CharField(required=False)
    expiration = forms.CharField(required=False)
    cvv = forms.CharField(required=False)
    number = forms.CharField(required=False)
    shipping_country = forms.CharField(required=False)
    shipping_zip = forms.CharField(required=False)

class CartForm(forms.Form):
    cart_quantity = forms.DecimalField(max_digits=5,decimal_places=2)

class QueryForm(forms.Form):
    query = forms.CharField()

class SupportForm(forms.Form):
    name = forms.CharField()
    message = forms.CharField()

class TestForm(forms.Form):
    message = forms.CharField()
    
class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()
