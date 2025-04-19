from django import forms
from django.utils.translation import gettext_lazy as _

class DailyContributionForm(forms.Form):
    amount = forms.DecimalField(label=_("Amount"), widget=forms.NumberInput(attrs={'placeholder': _("Enter amount"),"class":"form-control"}), required=True, max_digits=6, decimal_places=2)