from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import EmailMessage, send_mail
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import PasswordResetTokenGenerator, default_token_generator
from django.db.models import Avg

from Home.form import ReviewForm
from .forms import *
from .models import *
from Home.models import *


class EmailToken(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.is_active) + str(user.id) + str(timestamp)


email_generator = EmailToken()


def user_registration(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            firstname = form.cleaned_data['firstname']
            lastname = form.cleaned_data['lastname']
            email = form.cleaned_data['email']
            password2 = form.cleaned_data['password2']
            user = User.objects.create_user(
                username=username,
                first_name=firstname,
                last_name=lastname,
                email=email,
                password=password2,
            )
            user.is_active = False
            user.save()
            domain = get_current_site(request).domain
            uidb64 = urlsafe_base64_encode(force_bytes(user.id))
            token = default_token_generator.make_token(user)
            activation_link = f'https://{domain}/activate/{uidb64}/{token}'
            EmailMessage('فعال‌سازی حساب آچارین', activation_link, to=[email]).send()
            messages.success(request, 'لینک فعال‌سازی حساب برای شما ارسال شد.')
            return redirect('accounts:login')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save(update_fields=['is_active'])
        messages.success(request, 'حساب کاربری شما فعال شد.')
        return redirect('accounts:login')

    messages.error(request, 'لینک فعال‌سازی معتبر نیست یا منقضی شده است.')
    return redirect('accounts:user_registration')


def login_user(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(request, username=data['username'], password=data['password'])
            if user is None:
                try:
                    username = User.objects.get(email=data['username']).username
                except User.DoesNotExist:
                    username = None
                if username:
                    user = authenticate(request, username=username, password=data['password'])

            if user is not None:
                login(request, user)
                return redirect('home:homes')

            form.add_error(None, 'نام کاربری، ایمیل یا رمز عبور صحیح نیست.')
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('accounts:login')


@login_required(login_url='accounts:login')
def profile(request):
    user = request.user
    profiles, _ = Profile.objects.get_or_create(user=user)
    list_order = Factor.objects.filter(client_fact__user=user).order_by('-date_created')

    if request.method == 'POST':
        form_profile = FormProfile(request.POST, request.FILES, instance=profiles)
        form_user = FormUser(request.POST, instance=user)
        if form_profile.is_valid() and form_user.is_valid():
            form_user.save()
            form_profile.save()
            messages.success(request, 'اطلاعات حساب کاربری با موفقیت ذخیره شد.')
            return redirect('accounts:profile')
    else:
        form_profile = FormProfile(instance=profiles)
        form_user = FormUser(instance=user)

    return render(request, 'accounts/Profile.html', {
        'profiles': profiles,
        'form_user': form_user,
        'form_profile': form_profile,
        'list_order': list_order,
    })


@login_required(login_url='accounts:login')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'رمز عبور با موفقیت تغییر کرد.')
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_pass.html', {'form': form})


def custom_password_reset_request(request):
    if request.method == 'POST':
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = None

            if user:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_link = request.build_absolute_uri(
                    reverse('accounts:password_reset_confirm', args=[uid, token])
                )
                send_mail(
                    'بازیابی رمز عبور آچارین',
                    f'برای تغییر رمز عبور از لینک زیر استفاده کنید:\n{reset_link}',
                    'fahime.s310@gmail.com',
                    [email],
                    fail_silently=False,
                )
            return render(request, 'accounts/password_reset_done.html')
    else:
        form = CustomPasswordResetForm()
    return render(request, 'accounts/password_reset_form.html', {'form': form})


def password_reset_confirm(request, uidb64, token, password=None):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = CustomSetPasswordForm(request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data['new_pass1'])
                user.save()
                return render(request, 'accounts/password_reset_complete.html')
        else:
            form = CustomSetPasswordForm()
        return render(request, 'accounts/password_reset_confirm.html', {'form': form})

    return redirect('accounts:login')


def history(request):
    invoices = Factor.objects.filter(client_fact__user=request.user).order_by('-date_created')
    return render(request, 'accounts/history.html', {'invoices': invoices})


def detail_history(request, id):
    history_detail = get_object_or_404(Factor, id=id, client_fact__user=request.user)
    factor_services = history_detail.factor_services.select_related('service').prefetch_related('part_usages__part')
    reviews = set(history_detail.reviews.values_list('service_id', flat=True))
    for factor_service in factor_services:
        factor_service.has_review = factor_service.service_id in reviews
    return render(request, 'accounts/detail_history.html', {
        'history_detail': history_detail,
        'factor_services': factor_services,
    })


def submit_review(request, factor_id, service_id):
    factor = get_object_or_404(Factor, id=factor_id, client_fact__user=request.user)
    factor_service = get_object_or_404(FactorService, factor=factor, service_id=service_id)
    service = factor_service.service
    existing_review = Review.objects.filter(factor=factor, service=service).first()

    if existing_review:
        return redirect('accounts:detail_history', factor.id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.factor = factor
            review.service = service
            review.save()
            messages.success(request, 'نظر شما با موفقیت ثبت شد.')
            return redirect('accounts:detail_history', factor.id)
    else:
        form = ReviewForm()

    return render(request, 'accounts/submit_review.html', {
        'form': form,
        'factor': factor,
        'service': service,
        'factor_service': factor_service,
    })
