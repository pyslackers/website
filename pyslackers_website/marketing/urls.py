from django.urls import path

from .views import Index, TermsOfService, version


app_name = 'marketing'

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('terms/', TermsOfService.as_view(), name='tos'),
    path('version/', version, name='version')
]
