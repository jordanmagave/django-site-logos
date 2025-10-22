# urls.py
from django.urls import path
from . import views

app_name = "boletos"

urlpatterns = [
    path("", views.ConsultaBoletoView.as_view(), name="consulta"),
    path(
        "download/<int:boleto_id>/", views.DownloadBoletoView.as_view(), name="download"
    ),
]
