from django.contrib import admin
from .models import *
from django import forms


# Register your models here.


class ServicesAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')


class Sub_newAdmin(admin.ModelAdmin):
    list_display = ('sub_titer', 'sub_summary', 'reading_time')


class NewsAdmin(admin.ModelAdmin):
    list_display = ('titer', 'create_date')


class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'Cname', 'tel')


class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('client', 'device_type', 'request_date')


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('service', 'factor', 'msg', 'rating', 'created_at', 'is_approved')


class FactorAdmin(admin.ModelAdmin):
    list_display = ('client_fact', 'total_with_tax')


class ThousandSeparatorInput(forms.TextInput):
    def format_value(self, value):
        if value is None:
            return ""
        try:
            value = int(value)
            return f"{value:,}"
        except:
            return value


class FactorFormAdmin(forms.ModelForm):
    class Meta:
        model = Factor
        fields = "__all__"
        widgets = {
            "price": ThousandSeparatorInput()
        }


class PartAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')


admin.site.register(Services, ServicesAdmin)
admin.site.register(ServiceRequest, ServiceRequestAdmin)
admin.site.register(Sub_news, Sub_newAdmin)
admin.site.register(News, NewsAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Factor, FactorAdmin)
admin.site.register(Part, PartAdmin)
