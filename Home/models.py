from django.db import models
from django.urls import reverse
from taggit.managers import TaggableManager
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.forms import ModelForm
from django.db.models import Avg


# Create your models here.


class Services(models.Model):
    title = models.CharField(max_length=50, verbose_name='عنوان')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    icon = models.ImageField(upload_to='services', null=True, blank=True, verbose_name='ایکون سرویس')
    img = models.ImageField(upload_to='services', null=True, blank=True, verbose_name='تصویر سرویس')
    create_date = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name='تاریخ ایجاد')
    update_date = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name='تاریخ ویرایش')

    class Meta:
        verbose_name = 'خدمت'
        verbose_name_plural = " خدمات"

    def __str__(self):
        return self.title


class News(models.Model):
    titer = models.CharField(max_length=50, verbose_name='تیتر خبر ')
    slug = models.SlugField(unique=True, blank=True, allow_unicode=True)
    create_date = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name='تاریخ ایجاد')
    update_date = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name='تاریخ ویرایش')

    class Meta:
        verbose_name = 'عنوان خبر'
        verbose_name_plural = " عنوان اخبار"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titer, allow_unicode=True)
            super().save(*args, **kwargs)

    def __str__(self):
        return self.titer


class Sub_news(models.Model):
    new = models.ForeignKey(News, on_delete=models.CASCADE, related_name='services', verbose_name='دسته بندی اخبار')
    sub_titer = models.CharField(max_length=50, null=True, blank=True, verbose_name='عنوان')
    slug = models.SlugField(unique=True, blank=True, allow_unicode=True)
    sub_summary = models.TextField(max_length=20, blank=True, null=True, verbose_name='شرح مختصر')
    sub_description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    sub_create_date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    sub_update_date = models.DateTimeField(auto_now=True, verbose_name='تاریخ ویرایش')
    is_published = models.BooleanField(default=False)
    reading_time = models.PositiveSmallIntegerField(default=5, verbose_name='زمان مطالعه (دقیقه)')
    views = models.CharField(null=True, blank=True, verbose_name='تعداد مشاهده')
    sub_img = models.ImageField(upload_to='blog', null=True, blank=True, verbose_name='تصویر سرویس')

    class Meta:
        verbose_name = 'دسته بندی خبر'
        verbose_name_plural = " دسته بندی اخبار"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.sub_titer, allow_unicode=True)
        super().save(*args, **kwargs)

    from django.utils.text import slugify

    def __str__(self):
        return self.sub_titer


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='client',
                                verbose_name='کاربر')
    Cname = models.CharField(max_length=100, verbose_name='نام و نام خانوادگی مشتری')
    tel = models.CharField(max_length=11, unique=True, verbose_name='شماره تماس')

    class Meta:
        verbose_name = 'مشتری'
        verbose_name_plural = 'مشتری ها'

    def __str__(self):
        return self.Cname or self.tel


class ServiceRequest(models.Model):
    DEVICE_TYPE = [
        ('ref and freez', 'یخچال و فریزر'),
        ('laundry', 'ماشین لباسشویی'),
        ('dishwasher', 'ماشین ظرفشویی'),
        ('food procs', 'غذاساز'),
        ('coffe maker', 'قهوه ساز'),
        ('others', 'سایر'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='requests', verbose_name='مشتری')
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPE, verbose_name='نوع دستگاه')
    information = models.CharField(max_length=200, verbose_name='اطلاعات')
    request_date = models.DateField(auto_now_add=True, verbose_name='تاریخ درخواست')
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='زمان ثبت')

    class Meta:
        verbose_name = 'درخواست سرویس'
        verbose_name_plural = 'درخواست های سرویس'
        constraints = [
            models.UniqueConstraint(fields=['client', 'request_date'], name='one_request_per_client_per_day')
        ]

    def __str__(self):
        return f"{self.client} - {self.request_date}"


class Part(models.Model):
    name = models.CharField(max_length=200, verbose_name='نام قطعه')
    price = models.PositiveIntegerField(verbose_name='هزینه')

    class Meta:
        verbose_name = 'قطعه'
        verbose_name_plural = 'قطعات'

    def __str__(self):
        return self.name


class Factor(models.Model):
    client_fact = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='مشتری')
    services = models.ManyToManyField(Services, blank=True, related_name='factors', verbose_name='خدمات')
    parts = models.ManyToManyField(Part, blank=True, related_name='factors', verbose_name='قطعات')
    price_service = models.PositiveIntegerField(default=0, verbose_name='اجرت کل خدمات')
    tax_percent = models.PositiveIntegerField(default=9, verbose_name='درصد مالیات')
    date_created = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    @property
    def parts_total(self):
        return sum(part.price for part in self.parts.all())

    @property
    def total_without_tax(self):
        return self.price_service + self.parts_total

    @property
    def tax_amount(self):
        return (self.total_without_tax * self.tax_percent) / 100

    @property
    def total_with_tax(self):
        return self.total_without_tax + self.tax_amount

    class Meta:
        verbose_name = 'فاکتور'
        verbose_name_plural = 'فاکتورها'

    def __str__(self):
        return f'فاکتور {self.id}'


class Review(models.Model):
    factor = models.ForeignKey(Factor, on_delete=models.CASCADE, related_name='reviews', verbose_name='فاکتور')
    service = models.ForeignKey(Services, on_delete=models.CASCADE, related_name='reviews', verbose_name='خدمت')
    msg = models.TextField(max_length=600, verbose_name='نظر')
    rating = models.PositiveSmallIntegerField(default=5, verbose_name='امتیاز')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')
    is_approved = models.BooleanField(default=False, verbose_name='تایید پیام')

    class Meta:
        verbose_name = 'نظر'
        verbose_name_plural = 'نظرات'
        constraints = [
            models.UniqueConstraint(fields=['factor', 'service'], name='unique_review_per_factor_service')
        ]

    def __str__(self):
        return self.msg[:20]
