import datetime
from typing import Literal

from django.conf import settings
from django.utils import timezone
from django.db.models import Q


from sqlalchemy import create_engine, extract, or_, select
from sqlalchemy.orm import sessionmaker

from .models import SmsItem


def get_user_message_count(
    twillion_number: str, period: Literal["day", "month", "year"]
):
    from_date = datetime.date.today()
    if period == "day":
        from_date = from_date - datetime.timedelta(days=1)
    elif period == "month":
        from_date = from_date - datetime.timedelta(months=1)
    elif period == "year":
        from_date = from_date - datetime.timedelta(years=1)
    query = Q(SmsItem.sender_phone_number == twillion_number)
    query.add(Q(SmsItem.sender_phone_number == twillion_number), Q.OR)
    query.add(Q(SmsItem.sms_date__gte == from_date), Q.AND)
    SmsItem.objects.fitler(query).count()
