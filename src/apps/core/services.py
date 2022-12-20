import datetime
from typing import Literal

from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine, extract, or_, select
from sqlalchemy.orm import sessionmaker

from .models import SmsItem


def get_user_message_count(
    twillion_number: str, period: Literal["day", "month", "year"]
):
    from_date = datetime.date.today()
    if period == "day":
        from_date = from_date + relativedelta(days=-1)
    elif period == "month":
        from_date = from_date + relativedelta(months=-1)
    elif period == "year":
        from_date = from_date + relativedelta(years=-1)
    froms = SmsItem.objects.filter(
        sender_phone_number=twillion_number, sms_date__gt=from_date
    )
    sent = froms.count()
    received = SmsItem.objects.filter(
        recipient_phone_number=twillion_number, sms_date__gt=from_date
    ).count()
    return sent + received
