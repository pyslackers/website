from django.urls import path

from .views import task_result_view


app_name = 'core'

urlpatterns = [
    path('tasks/<uuid:task_id>', task_result_view, name='task-results'),
]
