from django.urls import path
from .views import HomeTemplateView, ContactTemplateView


app_name = "pages"

urlpatterns = [
    path("", view=HomeTemplateView.as_view(), name="index"),
    path("contact/", view=ContactTemplateView.as_view(), name="contact"),
]