# coding: utf-8
from django.db import models


class SmsItem(models.Model):
    __tablename__ = "sms_item"

    sms_id = models.IntegerField(primary_key=True, unique=True)
    user_email = models.CharField(max_length=50, null=False)
    recipient_phone_number = models.CharField(max_length=50, null=False)
    sender_phone_number = models.CharField(max_length=50, null=False)
    sms_date = models.DateField(null=False)
