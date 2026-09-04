import django_filters
from django import forms
from .models import *
from django import template

register = template.Library()


@register.filter
def star(rating, max_str=5):
    full = '*' * rating
    return full
