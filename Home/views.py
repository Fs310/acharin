from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import *
from .form import *
from accounts.models import *
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Count
from django.template.loader import render_to_string
from django.http import JsonResponse


# Create your views here.

def home(request):
    user = request.user
    if user.id:
        profiles = Profile.objects.get(user=user)
        form_profile = FormProfile(instance=profiles)
        form_user = FormUser(instance=user)
    else:
        form_profile = None
        form_user = None
    service = Services.objects.all()[:5]
    news = Sub_news.objects.all()[:4]
    review = Review.objects.filter(is_approved=True)[:6]
    return render(request, 'Home/home.html',
                  {'service': service, 'form_user': form_user, 'form_profile': form_profile, 'news': news,
                   'review': review})


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
    page_num = request.GET.get('page')
    page_obj = paginator.get_page(page_num)
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string(
            "Home/partials/service_cards.html",
            {
                "page_obj": page_obj
            },
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
    sub_news = Sub_news.objects.all()

    width = int(request.GET.get("width", 1920))

    if width >= 1400:
        per_page = 8
    elif width >= 992:
        per_page = 6
    elif width >= 768:
        per_page = 4
    else:
        per_page = 4
    paginator = Paginator(titer_news, per_page)
    page_num = request.GET.get('page')
    titer_news = paginator.get_page(page_num)

    if id:
        all_new = News.objects.get(id=id)
        sub_news = Sub_news.objects.filter(new=all_new)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string(
            "Home/partials/service_cards.html",
            {
                "titer_news": titer_news
            },
            request=request
        )

        return JsonResponse({
            "html": html,
            "has_next": titer_news.has_next()
        })
    return render(request, 'Home/news.html', {"titer_news": titer_news, 'sub_news': sub_news})


def detail_new(request, slug):
    new_detail = get_object_or_404(Sub_news, slug=slug)
    titer_news = News.objects.all()
    return render(request, 'Home/detail_new.html', {"titer_news": titer_news, 'new': new_detail})


def search_results(request):
    # product = Sub_Category.objects.all()
    # if request.method == 'POST':
    #     form = SearchForm(request.POST)
    #     if form.is_valid():
    #         data = form.cleaned_data['search']
    #         if data is not None:
    #             product = Sub_Category.objects.filter(name__icontains=data)
    # else:
    #     form = SearchForm()
    # return render(request, 'Home/home.html', {'form': form, 'all': product})
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

    return render(request, 'Home/home.html', {'client_form': client_form, 'request_form': request_form})


# def tracking_code(request):
#     form = TrackingCodeForm()
#     if request.method == 'POST':
#         form = TrackingCodeForm(request.POST)
#         if form.is_valid():
#             code = form.cleaned_data['code']
#             try:
#                 client = Client.objects.get(tracking_code=code)
#                 return redirect('add_review_guest', client_id=client.id)
#             except Client.DoesNotExist:
#                 messages.error(request, 'کد پیگیری معتبر نیست')
#     return render(request, 'home/enter_code.html', {'form': form})
def comments(request):
    comment = Review.objects.filter(is_approved=True).order_by('-created_at')
    avg_rating = comment.aggregate(average=Avg('rating'))['average']
    paginator = Paginator(comment, 6)
    page_num = request.GET.get('page')
    page_obj = paginator.get_page(page_num)
    return render(request, 'Home/comment.html', {'page_obj': page_obj, 'avg_rating': avg_rating, })


def about(request):
    return render(request, 'Home/about.html')


def contact(request):
    return render(request, 'Home/contact.html')
