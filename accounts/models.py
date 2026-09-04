from django.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='کاربر')
    address = models.TextField(blank=True, null=True, verbose_name='ادرس')
    tel = models.CharField(max_length=11, blank=True, null=True, verbose_name='تلفن')
    date_birthday = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ تولد')
    img_profile = models.ImageField(upload_to='profile', default='professional-img.png', verbose_name='عکس کاربر')

    class Meta:
        verbose_name = 'پروفایل'
        verbose_name_plural = " پروفایل ها"

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def save_profile_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class FormProfile(ModelForm):
    class Meta:
        model = Profile
        fields = ['address', 'tel', 'img_profile', 'date_birthday']


class FormUser(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

