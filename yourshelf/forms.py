from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from yourshelf.models import *

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )

class BookPackageForm(forms.Form):
    subscription_type = forms.CharField(max_length=254)
    book1 = forms.CharField(max_length=254)
    book2 = forms.CharField(max_length=254)
    #book3 = forms.CharField(max_length=254)
    #book4 = forms.CharField(max_length=254)

class BookRequestForm(forms.Form):
    book1 = forms.CharField(max_length=254)
    book2 = forms.CharField(max_length=254)
    book3 = forms.CharField(max_length=254)
    book4 = forms.CharField(max_length=254)

class BeforeCheckoutForm(forms.Form):
    subscription_type = forms.CharField(max_length=254)
    book1 = forms.CharField(max_length=254)
    book2 = forms.CharField(max_length=254)
    #book3 = forms.CharField(max_length=254)
    #book4 = forms.CharField(max_length=254)
    cardHolderName = forms.CharField(max_length=50)
    cardHolderSurname = forms.CharField(max_length=50)
    cardNumber = forms.CharField(max_length=19)
    expireMonth = forms.CharField(max_length=2)
    expireYear = forms.CharField(max_length=4)
    cvc = forms.CharField(max_length=3)
    gsmNumber = forms.CharField(max_length=20)
    email = forms.EmailField(max_length=254)
    identityNumber = forms.CharField(max_length=11)
    address = forms.CharField(max_length=500)
    city = forms.CharField(max_length=15)
    country = forms.CharField(max_length=15)
    zipCode = forms.CharField(max_length=5)

class BillingInformationForm(forms.ModelForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = BillingInformation
        fields = ('user', 'name', 'surname', 'gsm_number', 'email', 'identity_number',
                  'address', 'city', 'country', 'zipcode',)

class ImageUploadForm(forms.Form):
    image = forms.ImageField()