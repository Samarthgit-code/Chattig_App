from django import forms
from .models import Profile,Videos,Comment
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class ProfileForm(forms.ModelForm):
    class Meta:
        model=Profile
        fields='__all__'

class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = Videos
        fields = '__all__'

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

class RegisterForm(UserCreationForm):
    class Meta:
        model=User
        fields = ['username','email','password']
