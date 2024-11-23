import datetime

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm




class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='login', 
                               widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='password',
                               widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']



class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='login', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password1 = forms.CharField(label='password', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label='repeat password', widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'email': 'e-mail',
        }
        widgets = {
            'email': forms.TextInput(attrs={'class': 'form-input'})
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError('email already exists')
        return email
    

class ProfileUserForm(forms.ModelForm):
    username = forms.CharField(disabled=True, label='login', widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.CharField(disabled=True, label='email', widget=forms.TextInput(attrs={'class': 'form-input'}))

    this_year = datetime.date.today().year
    data_birth = forms.DateField(widget=forms.SelectDateWidget(years=tuple(range(this_year-100, this_year-5))))


    class Meta:
        model = get_user_model()
        fields = ['photo', 'username', 'data_birth', 'email']



class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label='Old password', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    new_password1 = forms.CharField(label='New password', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    new_password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput(attrs={'class': 'form-input'}))