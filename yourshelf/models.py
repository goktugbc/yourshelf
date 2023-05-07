from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime as dt
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

#-----------------------------Profile-----------------------------#

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(null=True, blank=True)
    email_confirmed = models.BooleanField(default=False)

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        BillingInformation.objects.create(user=instance)
    instance.profile.save()

#-----------------------------Subscription Type-----------------------------#

class SubscriptionType(models.Model):
    name_tr = models.CharField(default="", max_length=255, blank=True, null=True)
    name_en = models.CharField(default="", max_length=255, blank=True, null=True)
    period_tr = models.CharField(default="ay", max_length=5, blank=True, null=True)
    period_en = models.CharField(default="mo", max_length=5, blank=True, null=True)
    period_months = models.IntegerField(default=1, blank=True, null=True)
    price_tl = models.FloatField(default=24.90)
    price_usd = models.FloatField(blank=True, null=True)
    price_euro = models.FloatField(blank=True, null=True)
    deposit_tl = models.FloatField(default=30)
    deposit_usd = models.FloatField(blank=True, null=True)
    deposit_euro = models.FloatField(blank=True, null=True)
    number_of_books = models.IntegerField(default=4)
    photo_tr = models.ImageField()
    photo_en = models.ImageField()
    info_tr = models.TextField(default="")
    info_en = models.TextField(default="")
    shipment = models.BooleanField(default=True)
    active = models.BooleanField(default=True)

    def get_pricing_page_object(self, lang, currency):
        prices = {
            "TRY": self.price_tl,
            "USD": self.price_usd,
            "EUR": self.price_euro
        }

        deposits = {
            "TRY": self.deposit_tl,
            "USD": self.deposit_usd,
            "EUR": self.deposit_euro
        }

        signs = {
            "TRY": u"₺",
            "USD": u"$",
            "EUR": u"€"
        }

        info_texts = {
            "tr": self.info_tr,
            "en": self.info_en
        }

        names = {
            "tr": self.name_tr,
            "en": self.name_en
        }

        photos = {
            "tr": self.photo_tr.url,
            "en": self.photo_en.url
        }

        periods = {
            "tr": self.period_tr,
            "en": self.period_en
        }

        obj = {
            "id": urlsafe_base64_encode(force_bytes(self.id)).decode(),
            "name": names[lang],
            "price": prices[currency],
            "deposit": deposits[currency],
            "sign": signs[currency],
            "period": periods[lang],
            "number_of_books": self.number_of_books,
            "shipment": self.shipment,
            "photo": photos[lang],
            "info": info_texts[lang]
        }

        return obj


#-----------------------------Subscription-----------------------------#

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription_type = models.ForeignKey(SubscriptionType, on_delete=models.CASCADE)
    start_date = models.DateField(default=dt.now, blank=True, null=True)
    renewal_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    active = models.NullBooleanField(default=None)


#-----------------------------Book Selection-----------------------------#

class BookSelection(models.Model):
    book = models.TextField(default="", blank=True)
    sent = models.BooleanField(default=False)
    sent_date = models.DateField(blank=True, null=True)
    received = models.BooleanField(default=False)
    received_date = models.DateField(blank=True, null=True)

#-----------------------------Book Package-----------------------------#

class BookPackage(models.Model):
    books = models.ManyToManyField(BookSelection)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    request_date = models.DateField(blank=True, null=True)
    sent = models.BooleanField(default=False)
    sent_date = models.DateField(blank=True, null=True)
    cargo_tracking_code = models.CharField(default="", max_length=255, blank=True, null=True)

#-----------------------------Payment-----------------------------#

class Payment(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    token = models.CharField(default="", max_length=255, blank=True, null=True)
    total_paid = models.FloatField(blank=True, null=True)
    currency = models.CharField(default="TRY", max_length=10, blank=True, null=True)
    success = models.NullBooleanField(default=None)

#-----------------------------Billing Information-----------------------------#

class BillingInformation(models.Model):
    user =  models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(default="", max_length=255, blank=True, null=True)
    surname = models.CharField(default="", max_length=255, blank=True, null=True)
    gsm_number = models.CharField(default="", max_length=255, blank=True, null=True)
    identity_number = models.CharField(default="", max_length=11, blank=True, null=True)
    address = models.CharField(default="", max_length=500, blank=True, null=True)
    city = models.CharField(default="", max_length=15, blank=True, null=True)
    country = models.CharField(default="", max_length=15, blank=True, null=True)
    zipcode = models.CharField(default="", max_length=5, blank=True, null=True)

#-----------------------------Registered Card-----------------------------#

class RegisteredCard(models.Model):
    user =  models.OneToOneField(User, on_delete=models.CASCADE)
    card_token = models.CharField(default="", max_length=255, blank=True, null=True)
    card_user_key = models.CharField(default="", max_length=255, blank=True, null=True)