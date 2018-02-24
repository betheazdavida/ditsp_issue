from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# Register your models here.
from .models import Location, Informer, InformerOrigin, Division, Role, Member, Log, Complaint, Worker, ComplaintImages


class MemberInline(admin.StackedInline):
    model = Member


class NewUserAdmin(UserAdmin):
    inlines = [MemberInline]


admin.site.unregister(User)
admin.site.register(User, NewUserAdmin)
admin.site.register(Location)
admin.site.register(InformerOrigin)
admin.site.register(Informer)
admin.site.register(Complaint)
admin.site.register(Log)
admin.site.register(Member)
admin.site.register(Division)
admin.site.register(Role)
admin.site.register(Worker)
admin.site.register(ComplaintImages)
