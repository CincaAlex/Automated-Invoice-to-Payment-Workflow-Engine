from django.urls import path, include
from .views import home, upload_view, send_files

urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),
    path("upload/", upload_view, name="upload"),
    path("send_files/", send_files, name="send_files"),
    path("", home, name="home")
]
