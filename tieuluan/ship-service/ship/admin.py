from django.contrib import admin
from .models import ShippingMethod, Shipment
admin.site.register(ShippingMethod)
admin.site.register(Shipment)
