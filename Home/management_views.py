from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.forms import inlineformset_factory, modelform_factory
from django.shortcuts import get_object_or_404, redirect, render

from .models import (
    Services, ServiceItem, News, Sub_news, Client, ServiceRequest,
    Review, Factor, FactorService, PartUsage, Part,
)

MANAGEMENT_MODELS = {
    'services': ('خدمات', Services, ['title', 'description', 'icon', 'icon_hover', 'img']),
    'news': ('دسته‌بندی مقالات', News, ['titer']),
    'articles': ('مقالات', Sub_news, [
        'new', 'sub_titer', 'sub_summary', 'sub_description', 'is_published',
        'reading_time', 'views', 'sub_img',
    ]),
    'clients': ('مشتری‌ها', Client, ['user', 'Cname', 'tel']),
    'service-requests': ('درخواست‌های سرویس', ServiceRequest, ['client', 'device_type', 'information']),
    'reviews': ('نظرات', Review, ['factor', 'service', 'msg', 'rating', 'is_approved']),
    'parts': ('قطعات', Part, ['name', 'price']),
    'factors': ('فاکتورها', Factor, ['client_fact', 'tax_percent', 'is_issued']),
    'factor-services': ('اقلام فاکتور', FactorService, ['factor', 'service', 'price_service']),
    'part-usages': ('تعداد قطعات', PartUsage, ['factor_service', 'part', 'quantity', 'unit_price']),
}

def staff_required(view):
    @login_required
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, 'دسترسی به پنل مدیریت برای این حساب فعال نیست.')
            return redirect('home:homes')
        return view(request, *args, **kwargs)
    return wrapped

@staff_required
def management_dashboard(request):
    counts = {
        key.replace('-', '_'): model.objects.count()
        for key, (_, model, _) in MANAGEMENT_MODELS.items()
    }
    return render(request, 'Home/management/dashboard.html', {'counts': counts})

@staff_required
def management_list(request, section):
    if section not in MANAGEMENT_MODELS:
        return redirect('home:management_dashboard')
    title, model, _ = MANAGEMENT_MODELS[section]
    objects = model.objects.all()
    return render(request, 'Home/management/list.html', {
        'section': section,
        'title': title,
        'objects': objects,
        'model': model,
    })

@staff_required
def management_form(request, section, pk=None):
    if section not in MANAGEMENT_MODELS:
        return redirect('home:management_dashboard')
    title, model, fields = MANAGEMENT_MODELS[section]
    instance = get_object_or_404(model, pk=pk) if pk else None
    Form = modelform_factory(model, fields=fields)
    service_item_formset = None
    if section == 'services':
        ServiceItemFormSet = inlineformset_factory(
            Services, ServiceItem, fields=['title'], extra=1, can_delete=True
        )
        service_item_formset = ServiceItemFormSet(
            request.POST or None,
            instance=instance
        )
    if request.method == 'POST':
        form = Form(request.POST, request.FILES, instance=instance)
        if form.is_valid() and (service_item_formset is None or service_item_formset.is_valid()):
            with transaction.atomic():
                saved_instance = form.save()
                if service_item_formset is not None:
                    service_item_formset.instance = saved_instance
                    service_item_formset.save()
            messages.success(request, f'{title} با موفقیت ذخیره شد.')
            return redirect('home:management_list', section=section)
    else:
        form = Form(instance=instance)
    return render(request, 'Home/management/form.html', {
        'section': section,
        'title': title,
        'form': form,
        'instance': instance,
        'service_item_formset': service_item_formset,
    })

@staff_required
def management_delete(request, section, pk):
    if section not in MANAGEMENT_MODELS:
        return redirect('home:management_dashboard')
    title, model, _ = MANAGEMENT_MODELS[section]
    instance = get_object_or_404(model, pk=pk)
    if request.method == 'POST':
        instance.delete()
        messages.success(request, f'{title} حذف شد.')
        return redirect('home:management_list', section=section)
    return render(request, 'Home/management/delete.html', {
        'section': section,
        'title': title,
        'instance': instance,
    })
