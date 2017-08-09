from django.conf.urls import url

from .views import SlackInvite


urlpatterns = [
    url(r'^$', SlackInvite.as_view(), name='index'),
]
