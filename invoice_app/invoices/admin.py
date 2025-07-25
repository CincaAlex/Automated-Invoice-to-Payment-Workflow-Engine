from django.contrib import admin
from .models import Invoice, UploadFile, RejectedFile, Log

admin.site.register(Invoice)
admin.site.register(UploadFile)
admin.site.register(RejectedFile)
admin.site.register(Log)