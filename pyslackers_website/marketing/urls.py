from django.conf.urls import url

from .views import Index, TermsOfService, version


app_name = 'marketing'

urlpatterns = [
    url(r'^$', Index.as_view(), name='index'),
    url(r'^terms/$', TermsOfService.as_view(), name='tos'),
    url(r'^version/$', version, name='version')
]
