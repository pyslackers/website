from django.urls import path

from .views import SlackInvite, timezone_json_view, monthlymemberships_json_view


app_name = 'slack'

urlpatterns = [
    path('', SlackInvite.as_view(), name='index'),
    path('api/timezones', timezone_json_view, name='timezones'),
    path('api/monthlymemberships', monthlymemberships_json_view, name='monthlymemberships'),
]
