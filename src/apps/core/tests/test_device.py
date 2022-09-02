from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from apps.core.models import Device


user_model = get_user_model()

user_data = {
    "email": "softformanse@gmail.com",
    "full_name": "softformanse test",
    "password": "testpwd",
}

device_data = {
    "serial_number": "123456",
    "used": False,
    "nickname": "Test device",
}

device2_data = {
    "serial_number": "1234567",
    "used": False,
    "nickname": "Test device",
}


class TestDeviceCase(TestCase):
    def setUp(self) -> None:
        self.user = user_model.objects.create(
            full_name=user_data["full_name"],
            email=user_data["email"],
        )
        self.user.is_active = True
        self.user.set_password(user_data["password"])
        self.user.save()

    def test_device_creation(self):
        device = Device.objects.create(**device_data)
        self.assertEqual(Device.objects.all().count(), 1)
        self.assertIsNone(device.user)
        self.assertEqual(device.serial_number, device_data["serial_number"])
        self.assertEqual(device.nickname, device_data["nickname"])
        self.assertFalse(device.is_used, device_data["used"])
        device.set_nickname("Test change nickname")
        self.assertEqual(device.nickname, "Test change nickname")

    def test_device_not_exists(self):
        cant_register_device, message = Device.objects.can_register_device(
            device_data["serial_number"]
        )
        self.assertFalse(cant_register_device)
        self.assertEqual(
            message, "Device with this serial number does not exist"
        )

        device = Device.objects.create(**device_data)

        can_register_device, message = Device.objects.can_register_device(
            device.serial_number
        )
        self.assertTrue(can_register_device)

    def test_device_assign(self):
        device = Device.objects.create(**device_data)
        device.assign_to_user(self.user)
        device.save()

        can_register_device, message = Device.objects.can_register_device(
            device.serial_number
        )

        self.assertTrue(device.is_used)
        self.assertFalse(can_register_device)
        self.assertEqual(message, "Device with this serial number is used")
        self.assertEqual(device.user.id, self.user.id)

        Device.objects.delete_user_device(self.user)
        device = Device.objects.get(pk=device.id)
        self.assertFalse(device.is_used)
        self.assertIsNone(device.nickname)
        self.assertIsNone(device.user)

    def test_device_replace(self):
        device1 = Device.objects.create(**device_data)
        device2 = Device.objects.create(**device2_data)

        device1.assign_to_user(self.user)
        device1.set_nickname("device 1")
        device1.save()

        self.assertTrue(self.user.have_device)
        self.assertTrue(device1.is_used)
        self.assertEqual(self.user.id, device1.user.id)

        Device.objects.delete_user_device(self.user)

        device1 = Device.objects.get(
            serial_number=device_data["serial_number"]
        )

        self.assertFalse(device1.is_used)

        device2.assign_to_user(self.user)
        device2.set_nickname("device 2")
        device2.save()

        self.assertTrue(self.user.have_device)
        self.assertFalse(device1.is_used)
        self.assertTrue(device2.is_used)
        self.assertEqual(self.user.id, device2.user.id)

    def test_change_device_info(self):
        device = Device.objects.create(**device_data)
        self.assertEqual(device.serial_number, device_data["serial_number"])
        self.assertEqual(device.nickname, device_data["nickname"])
        device.set_nickname("test change nickname")
        device.serial_number = device2_data["serial_number"]
        device.save()
        self.assertEqual(device.nickname, "test change nickname")
        self.assertEqual(device.serial_number, device2_data["serial_number"])
