from django.conf.urls import url

from .views import Index, TermsOfService, info


urlpatterns = [
    url(r'^$', Index.as_view(), name='index'),
    url(r'^terms/$', TermsOfService.as_view(), name='tos'),
    url(r'^info/$', 'info', name="info")
]
