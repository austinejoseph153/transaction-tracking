from django.db import models
from apps.user.models import User
from django.utils.translation import gettext_lazy as _
import uuid
import datetime
from django.conf import settings

class DailyContribution(models.Model):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    STATUS_CHOICES = (
        (PENDING,"PENDING"),
        (SUCCESS, "SUCCESS"),
        (FAILED, "FAILED")
    )
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Customer"))
    amount = models.DecimalField(default=0.0, max_digits=6, decimal_places=2, verbose_name=("Transaction Amount"))
    date = models.DateTimeField(auto_now_add=True, verbose_name=_("Transaction Date"))
    status = models.CharField(max_length=20, default="pending", choices=STATUS_CHOICES, verbose_name=_("Transaction Status"))
    updated_at = models.DateTimeField(auto_now=True)
    notification = models.ForeignKey("transaction.notification", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.date}"
    
    class Meta:
        verbose_name = _("Daily Contribution")
        verbose_name_plural = _("Daily Contributions")
        ordering = ['-date']

class FailedTransaction(models.Model):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"
    REJECTED = "rejected"

    STATUS_CHOICES = (
        (PENDING,"PENDING"),
        (UNDER_REVIEW, "UNDER_REVIEW"),
        (RESOLVED, "RESOLVED"),
        (REJECTED, "REJECTED"),
    )
    
    contribution = models.ForeignKey(DailyContribution, on_delete=models.CASCADE)
    failure_reason = models.CharField(max_length=500)
    detected_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default="pending", choices=STATUS_CHOICES)
    resolved_at = models.DateTimeField(blank=True, null=True, verbose_name=_("Resolution Date"))
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Resolved By"), blank=True, null=True)
    notes = models.TextField(verbose_name=_("Resolution Notes"), blank=True, null=True)
    notification = models.ForeignKey("transaction.notification", on_delete=models.CASCADE, blank=True, null=True)
    charge_back_submitted = models.BooleanField(default=False, verbose_name=_("Chargeback Submitted"))
    
    def __str__(self):
        return f"{self.contribution.user.username} - {self.failure_reason} - {self.detected_at}"

    class Meta:
        verbose_name = _("Failed Transaction")
        verbose_name_plural = _("Failed Transactions")
        ordering = ['-detected_at']

class ChargebackForm(models.Model):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"
    REJECTED = "rejected"

    STATUS_CHOICES = (
        (SUBMITTED,"SUBMITTED"),
        (UNDER_REVIEW, "UNDER_REVIEW"),
        (RESOLVED, "RESOLVED"),
        (REJECTED, "REJECTED"),
    )
    failed_transaction = models.ForeignKey(FailedTransaction, on_delete=models.CASCADE)
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    submission_time = models.DateTimeField(auto_now_add=True)
    explanation = models.TextField()
    status = models.CharField(max_length=20, default="submitted", choices=STATUS_CHOICES)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="reviewer")
    review_time = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True, null=True) 
    notification = models.ForeignKey("transaction.notification", on_delete=models.CASCADE, blank=True, null=True)
    
    def __str__(self):
        return f"{self.submitted_by.username} - {self.status} - {self.submission_time}"

    class Meta:
        verbose_name = _("Chargeback Form")
        verbose_name_plural = _("Chargeback Forms")
        ordering = ['-submission_time']

class Notification(models.Model):
    """
     EmailQueue model
    """
    DAILY_CONTRIBUTION = 1
    FAILED_TRANSACTION = 2
    CHARGE_BACK_FORM = 3
    EMAIL_REASONS = (
        (DAILY_CONTRIBUTION, "DAILY CONTRIBUTION"),
        (FAILED_TRANSACTION, "FAILED TRANSACTION"),
        (CHARGE_BACK_FORM, "CHARGE BACK FORM"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255, verbose_name=_("Email Subject"))
    from_email = models.EmailField(verbose_name=_("From Email"))
    recipient = models.TextField(verbose_name=_("Recipient Email"))
    message = models.TextField()
    type = models.IntegerField(default=1)
    sent = models.BooleanField(default=False, verbose_name=_("Email Sent"))
    date = models.DateTimeField(default=datetime.datetime.today, verbose_name=_("Date Sent"))

    def __str__(self):
        return self.user.get_full_name()
    
    def get_email_type(self):
        email_type = None
        if self.type == 1:
            email_type = "DAILY CONTRIBUTION"
        elif self.type == 2:
            email_type = "FAILED TRANSACTION"
        elif self.type == 3:
            email_type = "CHARGE BACK FORM"
        return email_type

    class Meta:
        ordering = ["-date"]