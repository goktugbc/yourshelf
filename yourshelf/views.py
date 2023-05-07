# -*- coding: utf-8 -*-

from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseBadRequest
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, reverse
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm

import json

from yourshelf.models import *
from yourshelf.utils import *
from yourshelf.iyzico import Iyzico
from yourshelf.forms import SignUpForm, BookPackageForm, BeforeCheckoutForm, BillingInformationForm, BookRequestForm, ImageUploadForm
from yourshelf.tokens import account_activation_token

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('profile')
    else:
        return auth_views.login(request, template_name='login.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate Your Yourshelf Account'
            message = render_to_string('account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            send_mail(subject, message, ["hello@yourshelf.co"], [user.email])
            return redirect('login')
    else:
        if request.user.is_authenticated:
            return redirect('profile')
        else:
            form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('pricing')
    else:
        #return render(request, 'account_activation_invalid.html') #TODO bu sayfa hazirlanacak
        return redirect('signup')

def pricing(request):
    if request.user.is_authenticated:
        subscription = Subscription.objects.filter(user=request.user, active=True)
        if subscription:
            return redirect('profile')
    else:
        subscription = None
    subscription_type_objects = SubscriptionType.objects.filter(active=True)

    col_size = 12 / len(subscription_type_objects) if len(subscription_type_objects) > 2 else 4

    subscription_types = []
    constant = 1
    for obj in subscription_type_objects:
        pricing_page_object = obj.get_pricing_page_object("en", "TRY")
        pricing_page_object["col_size"] = int(col_size)
        pricing_page_object["col_offset_size"] = int(int(4) / int(len(subscription_type_objects) * constant))
        subscription_types.append(pricing_page_object)
        constant += 1

    return render(request, 'pricing.html', {'subscription_types': subscription_types, 'subscription': subscription})

def product(request, uidb64):
    if request.user.is_authenticated:
        subscription = Subscription.objects.filter(user=request.user, active=True)
        if subscription:
            return redirect('profile')
    if request.method == 'POST':
        if request.user.is_authenticated:
            form = BookPackageForm(request.POST)
            if form.is_valid():
                form_data = form.cleaned_data
                checkout_form = BeforeCheckoutForm()
                return render(request, 'before_checkout.html',
                              {'book1': form_data.get('book1'), 'book2': form_data.get('book2'),
                               #'book3': form_data.get('book3'), 'book4': form_data.get('book4'),
                               'subscription_type': form_data.get('subscription_type'), 'form': checkout_form
                               })
        else:
            form = SignUpForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                current_site = get_current_site(request)
                subject = 'Activate Your MySite Account'
                message = render_to_string('account_activation_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                    'token': account_activation_token.make_token(user),
                })
                user.email_user(subject, message)
                return redirect('login')
            else:
                return auth_views.login(request, template_name='login.html')
    else:
        id = urlsafe_base64_decode(uidb64).decode()
        product = SubscriptionType.objects.filter(id=id, active=True)
        if product:
            product = product[0]
            product_object = product.get_pricing_page_object("en", "TRY")
            if request.user.is_authenticated:
                book_package_form = BookPackageForm()
                return render(request, 'product.html', {'product_object': product_object, 'book_package_form': book_package_form})
            else:
                register_form = SignUpForm()
                login_form = AuthenticationForm()
                return render(request, 'product.html', {'product_object': product_object, 'register_form': register_form, 'login_form': login_form})
        else:
            return HttpResponseNotFound()



def checkout(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            form = BeforeCheckoutForm(request.POST)
            print(request.POST)
            if form.is_valid():
                form_data = form.cleaned_data
                id = urlsafe_base64_decode(form_data["subscription_type"]).decode()
                product = SubscriptionType.objects.filter(id=id, active=True)
                if product:
                    product = product[0]
                    iyzico = Iyzico()
                    ret_val = iyzico.create_card(request.user, product, form_data, "en", "TRY")
                    if ret_val[0]:
                        return redirect('profile')
                    else:
                        return redirect('pricing')
            else:
                return HttpResponseBadRequest()


@csrf_exempt
def iyzico_callback(request):
    iyzico = Iyzico()
    iyzico.check_checkout_form_result(request.POST["token"])
    return redirect('pricing')


def profile(request):
    if request.user.is_authenticated:
        subscription = Subscription.objects.filter(user=request.user, active=True)
        if subscription:
            subscription = subscription[0]

        if request.method == 'POST':
            billing_info = get_object_or_404(BillingInformation, user=request.user)
            billing_info_form = BillingInformationForm(request.POST, instance=billing_info)
            if billing_info_form.is_valid():
                billing_info_form.save()
                request.user.email = billing_info_form.cleaned_data.get('email')
                request.user.save()
            book_package_form = BookRequestForm(request.POST)
            if book_package_form.is_valid():
                form_data = book_package_form.cleaned_data

                book1 = BookSelection(book=form_data.get("book1"))

                book1.save()

                book2 = BookSelection(book=form_data.get("book2"))

                book2.save()

                book3 = BookSelection(book=form_data.get("book3"))

                book3.save()

                book4 = BookSelection(book=form_data.get("book4"))

                book4.save()

                book_package = BookPackage(subscription=subscription, request_date=dt.now())

                book_package.save()

                book_package.books.add(book1)
                book_package.books.add(book2)
                book_package.books.add(book3)
                book_package.books.add(book4)

                book_package.save()
            password_form = SetPasswordForm(request.user, request.POST)
            if password_form.is_valid():
                password_form.save()
            image_form = ImageUploadForm(request.POST, request.FILES)
            if image_form.is_valid():
                profile = Profile.objects.get(user=request.user)
                profile.photo = image_form.cleaned_data['image']
                profile.save()
            billing_info_form = BillingInformationForm()
            book_package_form = BookRequestForm()
            password_form = SetPasswordForm(request.user)
            return render(request, 'profile.html', {'billing_info_form': billing_info_form,
                                                    'book_package_form': book_package_form,
                                                    'password_form': password_form,
                                                    'subscription': subscription})
        else:
            billing_info_form = BillingInformationForm()
            book_package_form = BookRequestForm()
            password_form = SetPasswordForm(request.user)
            return render(request, 'profile.html', {'billing_info_form': billing_info_form,
                                                    'book_package_form': book_package_form, 'password_form': password_form,
                                                    'subscription': subscription})
    else:
        redirect('login')


def logout_redirect(request):

    return redirect('https://yourshelf.co')