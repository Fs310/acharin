from datetime import date, datetime
from django import template
from django.utils import timezone
import jdatetime

register = template.Library()

@register.filter
def to_jalali(value, date_format="%Y/%m/%d"):
    if not value:
        return ""
    try:
        if isinstance(value, datetime):
            if timezone.is_aware(value):
                value = timezone.localtime(value)
            return jdatetime.datetime.fromgregorian(datetime=value).strftime(date_format)
        if isinstance(value, date):
            return jdatetime.date.fromgregorian(date=value).strftime(date_format)
    except (TypeError, ValueError, OverflowError):
        return value
    return value
