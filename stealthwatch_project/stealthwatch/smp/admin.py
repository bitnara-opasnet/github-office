from django.contrib import admin
from .models import Profile, ApiConfig
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# Register your models here.
class ProfileAdmin(admin.StackedInline):
    model = Profile
    con_delete = False

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileAdmin,)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

class ApiConfigAdmin(admin.ModelAdmin):
    list_diaplay = ['ipaddress', 'username', 'password']

admin.site.register(ApiConfig, ApiConfigAdmin)    


