from django.contrib import admin
from yourshelf.models import *

class CustomModelAdminMixin(object):
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        super(CustomModelAdminMixin, self).__init__(model, admin_site)

@admin.register(Profile)
class ProfileAdmin(CustomModelAdminMixin, admin.ModelAdmin):
    pass

@admin.register(SubscriptionType)
class SubscriptionTypeAdmin(CustomModelAdminMixin, admin.ModelAdmin):
    pass

@admin.register(Subscription)
class SubscriptionAdmin(CustomModelAdminMixin, admin.ModelAdmin):
    pass

@admin.register(BookSelection)
class BookSelectionAdmin(CustomModelAdminMixin, admin.ModelAdmin):
    pass

@admin.register(BookPackage)
class BookPackageAdmin(CustomModelAdminMixin, admin.ModelAdmin):
    pass

@admin.register(Payment)
class PaymentAdmin(CustomModelAdminMixin, admin.ModelAdmin):
    pass

@admin.register(BillingInformation)
class BillingInformationAdmin(CustomModelAdminMixin, admin.ModelAdmin):
    pass

@admin.register(RegisteredCard)
class RegisteredCardAdmin(CustomModelAdminMixin, admin.ModelAdmin):
    pass