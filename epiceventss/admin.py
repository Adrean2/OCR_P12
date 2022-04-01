from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from epiceventss.models import User, Event, Contract, Client

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Event)
admin.site.register(Contract)
admin.site.register(Client)
