from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ["username", "email", "phone_number", "address", "created_at"]
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("phone_number", "address", "identity_document", "extracted_text")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("phone_number", "address", "identity_document")}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
