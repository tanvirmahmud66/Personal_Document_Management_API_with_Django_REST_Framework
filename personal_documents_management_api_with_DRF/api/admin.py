from django.contrib import admin
from .models import CustomUser, Documents


#=============================== Model List View
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ["id", "username", "email", "first_name", "last_name", "role","is_staff"]
    list_filter = ["role"]
    search_fields = ["id", "username", "email", "first_name", "last_name"]
    ordering = ["email", "id"]


class DocumentsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'creator', 'created_at','file')
    list_filter = ('title', 'creator', 'share_with', 'file')


#================================ model registration
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Documents, DocumentsAdmin)