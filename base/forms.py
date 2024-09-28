from django import forms
from .models import Room
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude=['host','participants']
        
        
class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','email']

class EmailUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    username = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ['email', 'username']

class RequestForm(forms.Form):
    request_id = forms.CharField(required=True)
