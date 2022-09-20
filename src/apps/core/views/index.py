# Create your views here.
from django.core.management import call_command
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from filer.models import (
    Clipboard,
    ClipboardItem,
    File,
    Folder,
    Image,
    ThumbnailOption,
)
from rest_framework.views import APIView


class IndexView(View):
    template_name = "index.html"

    def get(self, request):
        return render(request, self.template_name)


class CMSPagesViewset(APIView):
    def get(self, request):
        Clipboard.objects.all().delete()
        ClipboardItem.objects.all().delete()

        File.objects.all().delete()
        Folder.objects.all().delete()
        Image.objects.all().delete()
        ThumbnailOption.objects.all().delete()

        call_command("loaddata", "export.json")

        return HttpResponse("Uploaded")
