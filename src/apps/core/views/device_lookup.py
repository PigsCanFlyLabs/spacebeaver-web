from django import views
from django.http import JsonResponse

from apps.core.models import Device

from .device_owner import DeviceOwnerRequestSerializer


class DeviceLookup(views.View):
    def get(self, request):
        device_id = request.GET["device_id"]
        user = Device.objects.get(serial_number=device_id).user
        username = user.username
        return JsonResponse({"email": f"{username}@spacebeaver.com"})
