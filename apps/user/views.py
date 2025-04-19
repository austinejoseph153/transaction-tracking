from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.views.generic import FormView
from .auth import user_is_authenticated, user_logout, user_login, user_authenticate
from django.contrib import messages
from .forms import UserForm, LoginForm
from .utils import get_state_by_country_code_from_file,  get_countries_from_file
from django.utils.translation import gettext_lazy as _
from .models import User
from apps.transaction.models import DailyContribution, FailedTransaction, ChargebackForm

class CreateAccountTemplateView(TemplateView):
    template_name = "user/create_account.html"

    def render_to_response(self, context, **kwargs):
        response = super(CreateAccountTemplateView, self).render_to_response(context, **kwargs)
        return response
    
    def get_context_data(self, **kwargs):
        context = super(CreateAccountTemplateView, self).get_context_data(**kwargs)
        context["form"] = UserForm()
        context["user"] = user_is_authenticated(self.request)
        context["countries"] = get_countries_from_file()
        context["states"] = get_state_by_country_code_from_file("NG")
        return context
    
    def post(self, request, **kwargs): 
        context = {}
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            user = User(
                first_name=user_form.cleaned_data['first_name'],
                last_name=user_form.cleaned_data['last_name'],
                username=user_form.cleaned_data['username'],
                email=user_form.cleaned_data['email'],
                country=user_form.cleaned_data['country'],
                state=user_form.cleaned_data['state'],
                city=user_form.cleaned_data['city'],
                address=user_form.cleaned_data['address'],
                password=user_form.cleaned_data['password']
            )
            user.save()
            return redirect("user:login")
        else:
            context["form"] = user_form
            context["user"] = user_is_authenticated(request)
            context["countries"] = get_countries_from_file()
            context["states"] = get_state_by_country_code_from_file("NG")
            messages.error(request, _('Please fill the form correctly'))
            return super(CreateAccountTemplateView, self).render_to_response(context)

class LoginTemplateView(TemplateView):
    template_name = "user/login.html"

    def render_to_response(self, context, **kwargs):
        response = super(LoginTemplateView, self).render_to_response(context, **kwargs)
        return response
    
    def get_context_data(self, **kwargs):
        context = super(LoginTemplateView, self).get_context_data(**kwargs)
        context["form"] = LoginForm()
        context["user"] = user_is_authenticated(self.request)
        return context
    
    def post(self, request, **kwargs): 
        context = {}
        previous_url = request.session.get('previous_page' or None)
        redirected_urls = ["/daily/contribution/"]
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = user_authenticate(request, login_form.cleaned_data['username'], login_form.cleaned_data['password'])
            if user:
                user_login(request, user)
                if previous_url and previous_url in redirected_urls:
                    return redirect("/daily/contribution/")
                else:
                    messages.success(request, _("Login successful"))
                    return redirect("user:user_dashboard")
            else:
                context["form"] = login_form
                messages.error(request,_("Invalid Email or password!"))
                return super(LoginTemplateView, self).render_to_response(context)   
        else:
            context["form"] = login_form
            context["user"] = user_is_authenticated(request)
            messages.error(request, _('invalid username or password'))
            return super(CreateAccountTemplateView, self).render_to_response(context)


def logout(request):
    user_logout(request)
    messages.success(request, _('Logout was successful'))
    return redirect('user:login')


def user_dashboard(request):
    user = user_is_authenticated(request)
    if user:
        context = {}
        context["user"] = user
        return render(request,"user/dashboard/user_info.html", context=context)
    else:
        return redirect("user:login")

def user_contribution_list(request):
    user = user_is_authenticated(request)
    if user:
        context = {}
        contribution_list = DailyContribution.objects.filter(user=user)
        context["user"] = user
        context["contribution_list"] = contribution_list
        return render(request,"user/dashboard/contribution_list.html", context=context)
    else:
        return redirect("user:login")

def get_user_failed_transaction(request):
    user = user_is_authenticated(request)
    if user:
        context = {}
        failed_transactions = FailedTransaction.objects.filter(contribution__user=user)
        context["user"] = user
        context["failed_transactions"] = failed_transactions
        return render(request,"user/dashboard/failed_transaction.html", context=context)
    else:
        return redirect("user:login")

