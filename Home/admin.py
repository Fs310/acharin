from django.contrib import admin
from .models import *


class ServicesAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')


class Sub_newAdmin(admin.ModelAdmin):
    list_display = ('sub_titer', 'sub_summary', 'reading_time')


class NewsAdmin(admin.ModelAdmin):
    list_display = ('titer', 'create_date')


class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'Cname', 'tel')
    search_fields = ('Cname', 'tel', 'user__username')


class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('client', 'device_type', 'request_date')
    list_filter = ('device_type', 'request_date')
    search_fields = ('client__Cname', 'client__tel')


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('service', 'factor', 'rating', 'created_at', 'is_approved')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('service__title', 'factor__client_fact__Cname', 'msg')


class PartUsageInline(admin.TabularInline):
    model = PartUsage
    extra = 1
    fields = ('part', 'quantity', 'unit_price')

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.factor.is_issued:
            return ('part', 'quantity', 'unit_price')
        return ()

    def has_delete_permission(self, request, obj=None):
        if obj and obj.factor.is_issued:
            return False
        return super().has_delete_permission(request, obj)

    def get_extra(self, request, obj=None):
        if obj and obj.factor.is_issued:
            return 0
        return 1


class FactorServiceAdmin(admin.ModelAdmin):
    list_display = ('factor', 'service', 'price_service', 'parts_total', 'total')
    list_filter = ('service',)
    search_fields = ('factor__client_fact__Cname', 'factor__client_fact__tel', 'service__title')
    inlines = [PartUsageInline]

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.factor.is_issued:
            return ('factor', 'service', 'price_service')
        return ()

    def has_delete_permission(self, request, obj=None):
        if obj and obj.factor.is_issued:
            return False
        return super().has_delete_permission(request, obj)


class FactorAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'client_fact', 'date_created', 'is_issued',
        'services_total', 'parts_total', 'total_without_tax',
        'tax_amount', 'total_with_tax'
    )
    search_fields = ('client_fact__Cname', 'client_fact__tel')
    list_filter = ('is_issued', 'tax_percent', 'date_created')
    readonly_fields = ('services_total', 'parts_total', 'total_without_tax', 'tax_amount', 'total_with_tax')

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if obj and obj.is_issued:
            fields.append('is_issued')
            fields.extend(['client_fact', 'tax_percent'])
        return tuple(fields)


class PartAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)


admin.site.register(Services, ServicesAdmin)
admin.site.register(ServiceRequest, ServiceRequestAdmin)
admin.site.register(Sub_news, Sub_newAdmin)
admin.site.register(News, NewsAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Factor, FactorAdmin)
admin.site.register(Part, PartAdmin)
admin.site.register(FactorService, FactorServiceAdmin)
