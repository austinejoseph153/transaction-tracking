from django.urls import path
from .views import (DailyContributionTemplateView, daily_contribution_payment,
                     daily_contribution_success,ChargeBackFormTemplateView, 
                     cancel_daily_contribution, initiate_daily_contribution_payment)


app_name = "transaction"

urlpatterns = [
    path("chargeback/form/", view=ChargeBackFormTemplateView.as_view(), name="chargeback_form"),    
    path("daily/contribution/", view=DailyContributionTemplateView.as_view(), name="daily_contribution"),    
    path("daily/contribution/payment/<uuid:slug>/", view=daily_contribution_payment, name="daily_contribution_payment"),    
    path("initiate/payment/<uuid:slug>/", view=initiate_daily_contribution_payment, name="initiate_payment"),    
    path("cancel/daily/contribution/<uuid:slug>/", view=cancel_daily_contribution, name="cancel_daily_contribution"),    
    path("daily/contribution/success/<uuid:slug>/", view=daily_contribution_success, name="daily_contribution_success"),    
]