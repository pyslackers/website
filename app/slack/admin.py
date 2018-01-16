from django.contrib import admin

from .models import Invite, Membership


@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ('email', 'blocked', 'created_at')


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    date_hierarchy = 'timestamp'
    list_display = ('id', 'member_count', 'deleted_count', 'timestamp')
