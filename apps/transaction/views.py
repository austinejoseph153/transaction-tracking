from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.views.generic import FormView
from apps.user.auth import user_is_authenticated
from .forms import DailyContributionForm
from apps.user.models import User
import requests
from django.conf import settings
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import DailyContribution, FailedTransaction, ChargebackForm
from .utils import initiate_paystack_payment, initiate_flutterwave_payment
from .emails import send_notification

class DailyContributionTemplateView(TemplateView):
    template_name = "transaction/daily_contribution_form.html"

    def render_to_response(self, context, **kwargs):
        user = user_is_authenticated(self.request)
        if not user:
            return redirect("user:login")
        response = super(DailyContributionTemplateView, self).render_to_response(context, **kwargs)
        return response
    
    def get_context_data(self, **kwargs):
        context = super(DailyContributionTemplateView, self).get_context_data(**kwargs)
        context["user"] = user_is_authenticated(self.request)
        context["form"] = DailyContributionForm()
        return context
    
    def post(self, request, **kwargs):
        context = {}
        form = DailyContributionForm(request.POST)
        if form.is_valid():
            user = User.objects.get(pk=request.POST.get('user'))
            # Process the form data and save it to the database
            daily_contribution = DailyContribution(
                user=user,
                amount=form.cleaned_data['amount'],
            )
            daily_contribution.save()            
            return redirect("transaction:daily_contribution_payment", slug=daily_contribution.uuid)
        else:
            context["form"] = form
            context["user"] = user_is_authenticated(request)
            messages.error(request, _('Please fill the form correctly'))
            return super(DailyContributionTemplateView, self).render_to_response(context)

class ChargeBackFormTemplateView(TemplateView):
    template_name = "transaction/charge_back_form.html"

    def render_to_response(self, context, **kwargs):
        user = user_is_authenticated(self.request)
        if not user:
            return redirect("user:login")
        response = super(ChargeBackFormTemplateView, self).render_to_response(context, **kwargs)
        return response
    
    def get_context_data(self, **kwargs):
        context = super(ChargeBackFormTemplateView, self).get_context_data(**kwargs)
        context["user"] = user_is_authenticated(self.request)
        context["transaction_id"] = self.request.GET.get("transaction_id")
        return context
    
    def post(self, request, **kwargs):
        context = {}
        user_id = request.POST.get("user_id")
        transaction_id = request.POST.get("transaction_id")
        if not user_id or not transaction_id:
            messages.error(request, "sufficient information was not provided to perform this action")
            return super(ChargeBackFormTemplateView, self).render_to_response(context)
        submitted_by = User.objects.get(pk=user_id)
        transaction = FailedTransaction.objects.get(contribution__uuid=transaction_id)
        message = request.POST.get("message")
        if not message:
            messages.error(request,"please tell us the reason for submitting this charge back!")
            return super(ChargeBackFormTemplateView, self).render_to_response(context)
        if transaction.charge_back_submitted:
            messages.warning(request, "a query has already been submitted for this transaction")
            return redirect("user:user_dashboard")
        charge_back = ChargebackForm(
            failed_transaction=transaction,
            submitted_by = submitted_by,
            explanation = message

        )
        charge_back.save()
        # send notification for charge back to user
        email_message = """""
                    Hey, just a heads up - your recent transaction didn't go through. 
                    The payment failed due to an issue with your bank or card details. our team will
                    will attend to your complaints and you will be notified when the transaction has been resolved
        
                """
        send_notification(subject="CHARGEBACK FOR FAILED TRANSACTION", 
                          message=email_message,
                          recipient=submitted_by.email, 
                          user=submitted_by,
                          email_type=3)
        
        # redirect user to dashboard after submitting charge back form
        messages.success(request, "Charge back form submitted successfully")
        return redirect("user:user_dashboard")

# pament page for daily contribution 
def daily_contribution_payment(request, slug):
    user = user_is_authenticated(request)
    if not user:
        return redirect("user:login")
    context = {}
    daily_contribution = DailyContribution.objects.get(uuid=slug)
    context["user"] = user
    context["daily_contribution"] = daily_contribution
    return render(request, "transaction/daily_contribution_payment.html", context=context)

# initiate payment for daily contribution
def initiate_daily_contribution_payment(request, slug):
    user = user_is_authenticated(request)
    if not user:
        return redirect("user:login")
    daily_contribution = DailyContribution.objects.get(uuid=slug)
    payment = initiate_paystack_payment(
        ref_id=str(daily_contribution.uuid),
        amount=daily_contribution.amount,
        email=user.email,
        request=request
    )
    # payment = initiate_flutterwave_payment(
    #     tx_ref=str(daily_contribution.uuid),
    #     amount=int(daily_contribution.amount),
    #     email=user.email,
    #     full_name=user.get_full_name(),
    #     request=request
    # )
    # check if payment was successful
    if "link" in payment:
        # redirect users to payment link
        return redirect(payment["link"])
    else:
        # on payment failure, change contribution status to failed and save in database 
        daily_contribution.status = daily_contribution.FAILED
        daily_contribution.save()
        
        # create a failed transaction record and store in the database
        failure_reason = payment["error"] if payment["error"] else "error initializing paymeny"
        failed_transaction = FailedTransaction.objects.create(
            contribution = daily_contribution,
            failure_reason = failure_reason
        )

        # send notification for failed transaction to user
        message = """
                        Hey, just a heads up - your recent transaction didn't go through. 
                        The payment failed due to an issue with your bank or card details.
                        Don't worry, no money's been taken from your account. Try again or get in 
                        touch with our support team if you need help sorting it out
                    """
        notification = send_notification(
            subject="DAILY CONTRIBUTION FAILED",
            message=message,
            recipient=user.email,
            user=user,
            email_type=2

        )
        failed_transaction.notification = notification
        failed_transaction.save()
        messages.error()
        return redirect("transaction:daily_contribution_payment", slug=daily_contribution.uuid)
    

# cancel daily contribution
def cancel_daily_contribution(request, slug):
    user = user_is_authenticated(request)
    if not user:
        return redirect("user:login")
    try:
        daily_contribution = DailyContribution.objects.get(uuid=slug)
        daily_contribution.delete()
    except DailyContribution.DoesNotExist:
        messages.error(request, _('Daily Contribution not found'))
        return redirect("transaction:daily_contribution")
    
    messages.success(request, _('Daily Contribution Cancelled Successfully'))
    return redirect("transaction:daily_contribution")

# daliy contribution success
def daily_contribution_success(request, slug):
    user = user_is_authenticated(request)
    if not user:
        return redirect("user:login")
    
    context = {}
    daily_contribution = DailyContribution.objects.get(uuid=slug)
    daily_contribution.status = daily_contribution.SUCCESS
    daily_contribution.save()

    # check if email has already been sent for the transaction
    if not daily_contribution.notification:
        # send notification for failed transaction to user
        message = """
                    Success! Your transaction has been processed smoothly.
                    We've received confirmation that the payment's been made.
                    If you have any questions or concerns, our support team is here to help.
                    Thanks for saving with us!
                    """
        notification = send_notification(
                subject="DAILY CONTRIBUTION SUCCESSFUL",
                message=message,
                recipient=user.email,
                user=user,
                email_type=1
        )
        daily_contribution.notification = notification
        daily_contribution.save()
    
    context["user"] = user
    context["daily_contribution"] = daily_contribution
    return render(request, "transaction/daily_contribution_success.html", context=context)

