from django import forms
from django.contrib.auth.models import User


class UserRegisterForm(forms.Form):
    username = forms.CharField(max_length=50)
    email = forms.EmailField()
    firstname = forms.CharField(max_length=50)
    lastname = forms.CharField(max_length=50)
    password1 = forms.CharField(max_length=20)
    password2 = forms.CharField(max_length=20)

    def clean_username(self):
        user = self.cleaned_data.get('username')
        if User.objects.filter(username=user).exists():
            raise forms.ValidationError('Exists username')
        return user

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Exists email')
        return email

    def clean_password2(self):
        password2 = self.cleaned_data.get('password2')
        password1 = self.cleaned_data.get('password1')
        if password2 != password1:
            raise forms.ValidationError('No confirm')
        elif len(password2) < 2:
            raise forms.ValidationError('Short pass')
        elif not any(x.isupper() for x in password2):
            raise forms.ValidationError('No Uppercase')
        return password2


class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(max_length=20)


class CustomPasswordResetForm(forms.Form):
    email = forms.EmailField(
        label='Your Email:',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': "enter"
        })
    )


class CustomSetPasswordForm(forms.Form):
    new_pass1 = forms.CharField(
        label='new pass',
        widget=forms.PasswordInput
    )
    new_pass2 = forms.CharField(
        label='confirmed new pass',
        widget=forms.PasswordInput
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_pass1')
        p2 = cleaned_data.get('new_pass2')

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Error')
        return cleaned_data


