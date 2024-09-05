
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegistrationForm(UserCreationForm):

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UploadForm(forms.Form):

    csv_file = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': 'form-control', 'placeholder':
        'Upload "geocoder.csv"', 'help_text': 'Choose a .csv file with objects to geocode to enter'}))