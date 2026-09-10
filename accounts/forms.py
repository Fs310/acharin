from django import forms
from django.contrib.auth.models import User


class UserRegisterForm(forms.Form):
    username = forms.CharField(max_length=50, label='نام کاربری')
    email = forms.EmailField(label='ایمیل')
    firstname = forms.CharField(max_length=50, label='نام')
    lastname = forms.CharField(max_length=50, label='نام خانوادگی')
    tel = forms.CharField(max_length=11, min_length=11, label='شماره تماس')
    password1 = forms.CharField(max_length=128, widget=forms.PasswordInput, label='رمز عبور')
    password2 = forms.CharField(max_length=128, widget=forms.PasswordInput, label='تکرار رمز عبور')

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('این نام کاربری قبلاً ثبت شده است.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('این ایمیل قبلاً ثبت شده است.')
        return email

    def clean_tel(self):
        tel = self.cleaned_data['tel'].strip().translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789'))
        if tel.startswith('+98'):
            tel = '0' + tel[3:]
        elif tel.startswith('98'):
            tel = '0' + tel[2:]
        if not tel.startswith('09') or len(tel) != 11 or not tel.isdigit():
            raise forms.ValidationError('شماره موبایل معتبر وارد کنید.')
        return tel

    def clean_password2(self):
        password2 = self.cleaned_data.get('password2')
        password1 = self.cleaned_data.get('password1')
        if password1 and password2 and password2 != password1:
            raise forms.ValidationError('تکرار رمز عبور یکسان نیست.')
        if password2 and len(password2) < 8:
            raise forms.ValidationError('رمز عبور باید حداقل ۸ کاراکتر باشد.')
        return password2


class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=150, label='نام کاربری یا ایمیل')
    password = forms.CharField(max_length=128, widget=forms.PasswordInput, label='رمز عبور')


class CustomPasswordResetForm(forms.Form):
    email = forms.EmailField(
        label='ایمیل',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ایمیل خود را وارد کنید'
        })
    )


class CustomSetPasswordForm(forms.Form):
    new_pass1 = forms.CharField(
        label='رمز عبور جدید',
        widget=forms.PasswordInput
    )
    new_pass2 = forms.CharField(
        label='تکرار رمز عبور جدید',
        widget=forms.PasswordInput
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_pass1')
        p2 = cleaned_data.get('new_pass2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('رمزهای عبور یکسان نیستند.')
        return cleaned_data
