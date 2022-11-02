import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import sessionmaker

from apps.core.outside_db.models import SmsItem
from apps.core.outside_db.services import get_user_message_count


user_model = get_user_model()
USERDATA = {
    "email": "softformanse@gmail.com",
    "full_name": "softformanse test",
    "password": "testpwd",
}


class TestMessageCountOnDashboard(TestCase):
    def setUp(self) -> None:
        engine = create_engine(settings.OUTSIDE_DATA_NETLOC)
        self.Session = sessionmaker(engine)

        self.user = user_model.objects.create(
            full_name=USERDATA["full_name"],
            email=USERDATA["email"],
            twillion_number="123456",
        )
        self.user.is_active = True
        self.user.set_password(USERDATA["password"])
        self.user.save()

        with self.Session() as session:
            session.query(SmsItem).filter(
                SmsItem.user_email == self.user.email
            ).delete(synchronize_session=False)
            session.commit()

    def create_messages(self):
        ids = [i for i in range(1, 13)]
        with self.Session() as session:
            items = [
                SmsItem(
                    sms_text=f"Test message {i}",
                    user_email=self.user.email,
                    sms_id=i * 10000,
                    sms_date=datetime.datetime(2022, i, 2),
                    sender_phone_number=self.user.twillion_number,
                    recipient_phone_number=self.user.twillion_number + f"{i}",
                )
                for i in ids
            ]
            session.add_all(items)

            session.commit()

    def test_message_count(self):
        daily_message_count = get_user_message_count(
            self.user.twillion_number, "day"
        )
        monthly_message_count = get_user_message_count(
            self.user.twillion_number, "month"
        )
        yearly_message_count = get_user_message_count(
            self.user.twillion_number, "year"
        )

        self.assertEqual(daily_message_count, 0)
        self.assertEqual(monthly_message_count, 0)
        self.assertEqual(yearly_message_count, 0)
        self.create_messages()

        daily_message_count = get_user_message_count(
            self.user.twillion_number, "day"
        )
        monthly_message_count = get_user_message_count(
            self.user.twillion_number, "month"
        )
        yearly_message_count = get_user_message_count(
            self.user.twillion_number, "year"
        )
        if datetime.date.today().day == 2:
            self.assertEqual(daily_message_count, 12)
        else:
            self.assertEqual(daily_message_count, 0)

        self.assertEqual(monthly_message_count, 1)
        self.assertEqual(yearly_message_count, 12)

    def tearDown(self):
        with self.Session() as session:
            session.query(SmsItem).filter(
                SmsItem.user_email == self.user.email
            ).delete(synchronize_session=False)
            session.commit()
