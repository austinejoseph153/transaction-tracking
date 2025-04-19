from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.views.generic import FormView
from apps.user.auth import user_is_authenticated
from .forms import ContactForm
from .models import Contact
from django.contrib import messages

class HomeTemplateView(TemplateView):
    template_name = "pages/index.html"

    def render_to_response(self, context, **kwargs):
        response = super(HomeTemplateView, self).render_to_response(context, **kwargs)
        return response
    
    def get_context_data(self, **kwargs):
        context = super(HomeTemplateView, self).get_context_data(**kwargs)
        context["user"] = user_is_authenticated(self.request)
        return context

class ContactTemplateView(TemplateView):
    template_name = "pages/contact.html"

    def render_to_response(self, context, **kwargs):
        response = super(ContactTemplateView, self).render_to_response(context, **kwargs)
        return response
    
    def get_context_data(self, **kwargs):
        context = super(ContactTemplateView, self).get_context_data(**kwargs)
        context["user"] = user_is_authenticated(self.request)
        context["form"] = ContactForm()
        return context
    
    def post(self, request, **kwargs):
        context = {}
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = Contact(**form.cleaned_data)
            contact.save()
            messages.success(request, "your message has been successfully submitted")
            return redirect("pages:contact")
        else:
            context["form"] = form
            context["user"] = user_is_authenticated(self.request)
        return super(ContactTemplateView, self).render_to_response(context)