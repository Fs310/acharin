from django.db import models
from Home.models import *
from django.forms import ModelForm
from django.utils import timezone


class Coupons(models.Model):
    code = models.CharField(max_length=100, null=True, blank=True,verbose_name='کوپن تخفیف')
    discount = models.IntegerField(default=0,verbose_name='درصد تخفیف')
    start_date = models.DateTimeField(verbose_name='تاریخ شروع تخفیف')
    end_date = models.DateTimeField(verbose_name='تاریخ پایان تخفیف')
    active = models.BooleanField(default=False,verbose_name='فعال')

    class Meta:
        verbose_name='کوپن تخفیف'
        verbose_name_plural= " کوپن های تخفیف"

    def __str__(self):
        return self.code

    def expire(self):
        now = timezone.now()
        return self.active and self.start_date <= now <= self.end_date


class CouponsForm(ModelForm):
    class Meta:
        model = Coupons
        fields = ['code']
