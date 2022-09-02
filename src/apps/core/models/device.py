from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class DeviceManager(models.Manager):
    def can_register_device(self, serial_number: str, user=None):
        try:
            device = self.get(serial_number=serial_number)
            can_used = (not device.used and device.user is None) or (
                device.used
                and user
                and device.user
                and device.user.id == user.id
            )
            return (
                can_used,
                "" if can_used else "Device with this serial number is used",
            )
        except self.model.DoesNotExist:
            return False, "Device with this serial number does not exist"

    def delete_user_device(self, user: User):
        device = self.get(user_id=user.id)
        device.user = None
        device.used = False
        device.nickname = None
        device.save()


class Device(models.Model):
    serial_number = models.CharField(max_length=100, unique=True)
    used = models.BooleanField(default=False)
    nickname = models.CharField(max_length=100, blank=True, null=True)
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="device",
    )

    objects = DeviceManager()

    def __str__(self):
        return f"Device: {self.serial_number}"

    def assign_to_user(self, user: User):
        if self.is_used and user and self.user.id != user.id:
            raise ValueError(f"{self.serial_number} already used")
        user_device = Device.objects.filter(user_id=user.id)
        for device in user_device:
            if device.serial_number != self.serial_number:
                raise ValueError(f"User: {user} already have device")
        self.user = user
        self.used = True

    def set_nickname(self, nickname: str):
        self.nickname = nickname

    @property
    def is_used(self):
        return self.used or self.user
