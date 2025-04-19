from django.urls import path
from .views import (CreateAccountTemplateView, user_dashboard,
                    LoginTemplateView, logout, user_contribution_list 
                    )
app_name = "user"

urlpatterns = [
    path("user/create-account/", view=CreateAccountTemplateView.as_view(), name="create_account"),
    path("login/", view=LoginTemplateView.as_view(), name="login"),
    path("user/dashboard/", view=user_dashboard, name="user_dashboard"),
    path("user/contributions/", view=user_contribution_list, name="user_contributions"),
    path("logout/", view=logout, name="logout"),
]