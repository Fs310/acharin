from .models import *
from django import forms


class SearchForm(forms.Form):
    search = forms.CharField(max_length=20)


def normalize_phone(value):
    value = value.strip()
    value = value.translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789'))

    if value.startswith('+98'):
        value = '0' + value[3:]
    elif value.startswith('98'):
        value = '0' + value[2:]

    return value


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['Cname', 'tel']

    def clean_tel(self):
        tel = normalize_phone(self.cleaned_data['tel'])

        if not tel.startswith('09') or len(tel) != 11 or not tel.isdigit():
            raise forms.ValidationError('شماره موبایل معتبر وارد کنید.')

        return tel


class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ['device_type', 'information']


class ReviewForm(forms.ModelForm):
    RATING_CHOICES = [(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')]

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect
    )

    class Meta:
        model = Review
        fields = ['msg', 'rating']

# class TrackingCodeForm(forms.Form):
#     code = forms.CharField(label='کدپیگیری')
