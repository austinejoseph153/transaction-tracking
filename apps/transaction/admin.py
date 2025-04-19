from django.contrib import admin
from .models import DailyContribution, FailedTransaction, ChargebackForm, Notification
from django.utils.translation import gettext_lazy as _

@admin.register(DailyContribution)
class DailyContributionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'date', 'status')
    list_filter = ('status', 'date')

@admin.register(FailedTransaction)
class FailedTransactionAdmin(admin.ModelAdmin):
    list_display = ('contribution', 'failure_reason', 'detected_at', 'resolved')
    list_filter = ('resolved', 'detected_at')
    search_fields = ('failure_reason',)
    actions = ['mark_as_resolved',]
    
    def mark_as_resolved(self, request, queryset):
        for transaction in queryset:
            transaction.resolved = True
            transaction.save()
        self.message_user(request, _("Selected transactions marked as resolved."))
    mark_as_resolved.short_description = _("Mark selected transactions as resolved")

@admin.register(ChargebackForm)
class ChargebackFormAdmin(admin.ModelAdmin):
    list_display = ('failed_transaction', 'submitted_by', 'status')
    list_filter = ('status', 'submission_time')
    search_fields = ('failed_transaction__failure_reason',)
    actions = ['mark_as_resolved', 'mark_as_rejected', 'mark_as_under_review']

    def mark_as_resolved(self, request, queryset):
        for form in queryset:
            form.status = ChargebackForm.RESOLVED
            form.save()
        self.message_user(request, _("Selected chargeback forms marked as resolved."))
    mark_as_resolved.short_description = _("Mark selected chargeback forms as resolved")

    def mark_as_rejected(self, request, queryset):
        for form in queryset:
            form.status = ChargebackForm.REJECTED
            form.save()
        self.message_user(request, _("Selected chargeback forms marked as rejected."))
    mark_as_rejected.short_description = _("Mark selected chargeback forms as rejected")

    def mark_as_under_review(self, request, queryset):
        for form in queryset:
            form.status = ChargebackForm.UNDER_REVIEW
            form.save()
        self.message_user(request, _("Selected chargeback forms marked as under review."))
    mark_as_under_review.short_description = _("Mark selected chargeback forms as under review")

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['email_type', 'customer_full_name', 'from_email', 'recipient', 'date', 'sent']

    def customer_full_name(self, obj):
        return obj.user.get_full_name()
    
    def email_type(self, obj):
        return obj.get_email_type()
    
    