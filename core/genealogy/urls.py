from django.urls import path
from .views import ComponentAPIView

urlpatterns = [
    path('component/', ComponentAPIView.as_view(), name='component-api'),
]
