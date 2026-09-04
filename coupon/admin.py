from django.contrib import admin
from .models import *


# Register your models here.

class CouponsAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'discount', 'start_date', 'end_date', 'active']


admin.site.register(Coupons, CouponsAdmin)
