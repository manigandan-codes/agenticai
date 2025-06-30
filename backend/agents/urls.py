from django.urls import path
from .views import *

urlpatterns = [
    path('', welcome, name='welcome'),
    path('process-feedback/', process_feedback, name='process_feedback'),
]
