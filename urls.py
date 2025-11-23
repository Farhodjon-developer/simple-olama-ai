from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="chat-index"),
    path("api/", views.api_chat, name="chat-api"),
]