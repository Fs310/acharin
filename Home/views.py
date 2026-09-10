from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Avg

from .models import *
from .form import *
from accounts.models import *


def home(request):
    user = request.user

    if user.is_authenticated:
        profiles, _ = Profile.objects.get_or_create(user=user)
        form_profile = FormProfile(instance=profiles)
        form_user = FormUser(instance=user)
    else:
        form_profile = None
        form_user = None

    service = Services.objects.all()[:5]
    news = Sub_news.objects.all()[:4]
    review = Review.objects.filter(is_approved=True).select_related('factor__client_fact', 'service')[:6]

    return render(request, 'Home/home.html', {
        'service': service,
        'form_user': form_user,
        'form_profile': form_profile,
        'news': news,
        'review': review,
    })


def service(request):
    services = Services.objects.all()
    width = int(request.GET.get("width", 1920))

    if width >= 1400:
        per_page = 8
    elif width >= 992:
        per_page = 6
    elif width >= 768:
        per_page = 4
    else:
        per_page = 4

    paginator = Paginator(services, per_page)
    page_obj = paginator.get_page(request.GET.get('page'))

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string(
            "Home/partials/service_cards.html",
            {'page_obj': page_obj},
            request=request
        )
        return JsonResponse({
            "html": html,
            "has_next": page_obj.has_next()
        })

    return render(request, 'Home/service.html', {'page_obj': page_obj})


def detail_service(request, id):
    service_detail = get_object_or_404(Services, id=id)
    return render(request, 'Home/detail_service.html', {'service': service_detail})


def new(request, id=None):
    titer_news = News.objects.all()
    sub_news = Sub_news.objects.all().select_related('new')

    if id:
        get_object_or_404(News, id=id)
        sub_news = sub_news.filter(new_id=id)

    width = int(request.GET.get("width", 1920))

    if width >= 1400:
        per_page = 8
    elif width >= 992:
        per_page = 6
    elif width >= 768:
        per_page = 4
    else:
        per_page = 4

    paginator = Paginator(sub_news, per_page)
    page_obj = paginator.get_page(request.GET.get('page'))

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string(
            "Home/partials/news_cards.html",
            {'page_obj': page_obj},
            request=request
        )
        return JsonResponse({
            "html": html,
            "has_next": page_obj.has_next()
        })

    return render(request, 'Home/news.html', {
        'titer_news': titer_news,
        'sub_news': page_obj,
        'page_obj': page_obj,
    })


def detail_new(request, slug):
    new_detail = get_object_or_404(Sub_news.objects.select_related('new'), slug=slug)
    titer_news = News.objects.all()
    related_articles = Sub_news.objects.filter(new=new_detail.new).exclude(pk=new_detail.pk)[:5]

    return render(request, 'Home/detail_new.html', {
        'titer_news': titer_news,
        'new': new_detail,
        'related_articles': related_articles,
    })


def search_results(request):
    return None


def clients(request):
    if request.method == 'POST':
        client_form = ClientForm(request.POST)
        request_form = ServiceRequestForm(request.POST)

        if client_form.is_valid() and request_form.is_valid():
            tel = client_form.cleaned_data['tel']
            cname = client_form.cleaned_data['Cname']
            today = timezone.localdate()

            client = Client.objects.filter(tel=tel).first()

            if client is None:
                client = Client.objects.create(
                    Cname=cname,
                    tel=tel,
                    user=request.user if request.user.is_authenticated else None
                )
            elif request.user.is_authenticated and client.user is None:
                client.user = request.user
                client.save(update_fields=['user'])

            if ServiceRequest.objects.filter(client=client, request_date=today).exists():
                messages.error(request, 'شما امروز قبلاً یک درخواست ثبت کرده‌اید.')
                return redirect('home:homes')

            service_request = request_form.save(commit=False)
            service_request.client = client
            service_request.save()

            messages.success(request, 'درخواست شما با موفقیت ثبت شد.')
            return redirect('home:homes')

    else:
        client_form = ClientForm()
        request_form = ServiceRequestForm()

    return render(request, 'Home/home.html', {
        'client_form': client_form,
        'request_form': request_form,
    })


def comments(request):
    comment = Review.objects.filter(is_approved=True).select_related('factor__client_fact', 'service').order_by('-created_at')
    avg_rating = comment.aggregate(average=Avg('rating'))['average']
    paginator = Paginator(comment, 6)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'Home/comment.html', {
        'page_obj': page_obj,
        'avg_rating': avg_rating,
    })


def about(request):
    return render(request, 'Home/about.html')


def contact(request):
    return render(request, 'Home/contact.html')
