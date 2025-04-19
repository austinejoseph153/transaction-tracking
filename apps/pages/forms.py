from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(label="Your Name", widget=forms.TextInput(attrs={"class":"form-control"}))
    phone = forms.CharField(label="Phone", widget=forms.TextInput(attrs={"class":"form-control"}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"class":"form-control"}))
    subject = forms.CharField(label="Subject", widget=forms.TextInput(attrs={"class":"form-control"}))
    message = forms.CharField(label="Subject", widget=forms.Textarea(attrs={"class":"form-control"}))
