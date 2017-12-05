from django.urls import path

from .views import SlackInvite


app_name = 'slack'

urlpatterns = [
    path('', SlackInvite.as_view(), name='index'),
]
