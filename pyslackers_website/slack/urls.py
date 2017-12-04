from django.conf.urls import url

from .views import SlackInvite


app_name = 'slack'

urlpatterns = [
    url(r'^$', SlackInvite.as_view(), name='index'),
]
