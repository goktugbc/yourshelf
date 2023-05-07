# -*- coding: utf-8 -*-

import iyzipay
from yourshelf.settings import IYZICO_API_KEY, IYZICO_SECRET_KEY, IYZICO_BASE_URL
from yourshelf.models import *

from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
import json

class Iyzico():
    api_key = IYZICO_API_KEY
    secret_key = IYZICO_SECRET_KEY
    base_url = IYZICO_BASE_URL

    def _init_(self):
        self.api_key = IYZICO_API_KEY
        self.secret_key = IYZICO_SECRET_KEY
        self.base_url = IYZICO_BASE_URL

    def subscription_start_payment_with_checkout_form(self, user, product, form_data, lang, currency):
        product_object = product.get_pricing_page_object(lang, currency)

        options = {
            'api_key': self.api_key,
            'secret_key': self.secret_key,
            'base_url': self.base_url
        }

        """
        payment_card = {
            'cardHolderName': u'Abdullah Göktuğ Mert',
            'cardNumber': '4506347027041579',
            'expireMonth': '10',
            'expireYear': '2022',
            'cvc': '467',
            'registerCard': '1'
        }
        """

        buyer = {
            'id': str(user.id),
            'name': form_data["name"],
            'surname': form_data["surname"],
            'gsmNumber': form_data["gsmNumber"],
            'email': form_data["email"],
            'identityNumber': form_data["identityNumber"],
            'registrationAddress': form_data["address"],
            'ip': '85.34.78.112',
            'city': form_data["city"],
            'country': form_data["country"],
            'zipCode': form_data["zipCode"]
        }

        address = {
            'contactName': form_data["name"] + " " + form_data["surname"],
            'city': form_data["city"],
            'country': form_data["country"],
            'address': form_data["address"],
            'zipCode': form_data["zipCode"]
        }

        basket_items = [
            {
                'id': str(product_object["id"]),
                'name': product_object["name"],
                'category1': 'subscription',
                'itemType': 'VIRTUAL',
                'price': str(product_object["price"])
            }
        ]

        if product_object["deposit"] > 0:
            basket_items.append({
                'id': str(product_object["id"]) + "-Deposit",
                'name': 'Deposit',
                'category1': 'deposit',
                'itemType': 'VIRTUAL',
                'price': str(product_object["deposit"])
            })

        """
        request = {
            'locale': 'tr',
            'conversationId': '123456789',
            'price': '1',
            'callbackUrl': 'google.com',
            'paidPrice': '1.2',
            'currency': 'TRY',
            'installment': '1',
            'basketId': 'B67832',
            'paymentChannel': 'WEB',
            'paymentGroup': 'PRODUCT',
            'paymentCard': payment_card,
            'buyer': buyer,
            'shippingAddress': address,
            'billingAddress': address,
            'basketItems': basket_items
        }
        """

        subscription = Subscription(user=user, subscription_type=product, start_date=dt.now(),
                                    renewal_date=dt.now() + relativedelta(months=1), active=None)

        subscription.save()

        book1 = BookSelection(book=form_data["book1"])

        book1.save()

        book2 = BookSelection(book=form_data["book2"])

        book2.save()

        #book3 = BookSelection(book=form_data["book3"])

        #book3.save()

        #book4 = BookSelection(book=form_data["book4"])

        #book4.save()

        book_package = BookPackage(subscription=subscription, request_date=dt.now())

        book_package.save()

        book_package.books.add(book1)
        book_package.books.add(book2)
        #book_package.books.add(book3)
        #book_package.books.add(book4)

        book_package.save()

        payment = Payment(subscription=subscription, total_paid=product_object["price"] + product_object["deposit"],
                          currency=currency)

        payment.save()

        request = {
            'locale': lang,
            'conversationId': str(payment.id),
            'price': str(product_object["price"] + product_object["deposit"]),
            'paidPrice': str(product_object["price"] + product_object["deposit"]),
            'installment': '1',
            'currency': currency,
            'basketId': str(book_package.id),
            'paymentGroup': 'SUBSCRIPTION',
            "callbackUrl": "http://127.0.0.1:8000/iyzico_callback/",
            'registerCard' : '1',
            'buyer': buyer,
            'shippingAddress': address,
            'billingAddress': address,
            'basketItems': basket_items
        }

        checkout_form_initialize = iyzipay.CheckoutFormInitialize().create(request, options)

        return json.loads(checkout_form_initialize.read().decode('utf-8'))["paymentPageUrl"]

    def create_card(self, user, product, form_data, lang, currency):
        #product_object = product.get_pricing_page_object(lang, currency)

        options = {
            'api_key': self.api_key,
            'secret_key': self.secret_key,
            'base_url': self.base_url
        }


        payment_card = {
            'cardAlias': str(user.id) + "-card",
            'cardHolderName': form_data["cardHolderName"] + " " + form_data["cardHolderSurname"],
            'cardNumber': form_data["cardNumber"].replace(" ",""),
            'expireMonth': form_data["expireMonth"] if len(form_data["expireMonth"]) == 2 else "0"+form_data["expireMonth"],
            'expireYear': '20' + form_data["expireYear"][-2:],
            'cvc': form_data["cvc"]
        }

        request = {
            'locale': lang,
            'email': form_data["email"],
            'card': payment_card
        }

        card = iyzipay.Card().create(request, options)

        result = json.loads(card.read())

        success = True if result["status"] == "success" else False

        billing_info = BillingInformation.objects.filter(user=user)

        if billing_info:
            billing_info.update(name=form_data["cardHolderName"], surname=form_data["cardHolderSurname"],
                                  gsm_number=form_data["gsmNumber"],
                                  identity_number=form_data["identityNumber"],
                                  address=form_data["address"], city=form_data["city"],
                                  country=form_data["country"],
                                  zipcode=form_data["zipCode"])
        else:
            billing_info = BillingInformation(name=form_data["cardHolderName"], surname=form_data["cardHolderSurname"],
                                              gsm_number=form_data["gsmNumber"], identity_number=form_data["identityNumber"],
                                              address=form_data["address"], city=form_data["city"], country=form_data["country"],
                                              zipcode=form_data["zipCode"])

            billing_info.save()

        user.email = form_data["email"]

        user.save()

        if success:
            message = "Success"

            card_token = result["cardToken"]

            card_user_key = result["cardUserKey"]

            card = RegisteredCard(user=user, card_token=card_token, card_user_key=card_user_key)

            card.save()

            subscription = Subscription(user=user, subscription_type=product, start_date=dt.now(),
                                        renewal_date=dt.now() + relativedelta(months=product.period_months), active=True)
            subscription.save()

            book1 = BookSelection(book=form_data["book1"])

            book1.save()

            book2 = BookSelection(book=form_data["book2"])

            book2.save()

            # book3 = BookSelection(book=form_data["book3"])

            # book3.save()

            # book4 = BookSelection(book=form_data["book4"])

            # book4.save()

            book_package = BookPackage(subscription=subscription, request_date=dt.now())

            book_package.save()

            book_package.books.add(book1)
            book_package.books.add(book2)
            # book_package.books.add(book3)
            # book_package.books.add(book4)

            book_package.save()
        else:
            message = result["errorMessage"]

        return success, message

    def check_checkout_form_result(self, token):
        options = {
            'api_key': self.api_key,
            'secret_key': self.secret_key,
            'base_url': self.base_url
        }

        request = {
            'token': token
        }

        checkout_form_result = iyzipay.CheckoutForm().retrieve(request, options)

        result = json.loads(checkout_form_result.read().decode('utf-8'))

        payment_id = result["conversationId"]

        payment = Payment.objects.get(id=payment_id)

        success = True if result["status"] == "success" else False

        payment.success = success

        payment.save()

        message = ""

        if success:
            user = payment.subscription.user

            card_token = result["cardToken"]

            card_user_key = result["cardUserKey"]

            card = RegisteredCard(user=user, card_token=card_token, card_user_key=card_user_key)

            card.save()

            payment.subscription.active = True

            payment.subscription.save()

            message = "Success"

        else:
            message = result["errorMessage"]

        return success, message