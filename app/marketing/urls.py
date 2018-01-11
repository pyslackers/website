from django.urls import path

from .views import (
    GoogleSearchVerificationView,
    Index,
    TermsOfService,
    version,
)


app_name = 'marketing'

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('google5e9627529a176ba5.html', GoogleSearchVerificationView.as_view()),
    path('terms/', TermsOfService.as_view(), name='tos'),
    path('version/', version, name='version')
]
