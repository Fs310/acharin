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
    list_display = (
        'id', 'client_fact', 'date_created', 'services_total', 'parts_total', 'total_without_tax', 'tax_amount',
        'total_with_tax')
    search_fields = ('client_fact__Cname', 'client_fact__tel')
    list_filter = ('tax_percent',)


def save_formset(request, form, formset, change):
    instances = formset.save(commit=False)
    for instance in instances:
        if instance.part and not instance.unit_price:
            instance.unit_price = instance.part.price
        instance.save()
    formset.save_m2m()


class PartUsageInline(admin.TabularInline):
    model = PartUsage
    extra = 1
    readonly_fields = ('unit_price',)
    fields = ('part', 'quantity', 'unit_price')


class FactorServiceAdmin(admin.ModelAdmin):
    list_display = ('factor', 'service', 'price_service', 'parts_total', 'total')
    list_filter = ('service',)
    search_fields = ('factor__client_fact__Cname', 'service__title')
    inlines = [PartUsageInline]


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
admin.site.register(FactorService, FactorServiceAdmin)
