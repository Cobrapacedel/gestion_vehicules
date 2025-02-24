# vehicles/admin.py
from django.contrib import admin
from .models import Brand, VehicleModel

admin.site.register(Brand)
admin.site.register(VehicleModel)

