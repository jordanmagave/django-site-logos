# services/cloud_storage.py
from google.cloud import storage
from django.conf import settings
import os
from datetime import timedelta


class CloudStorageManager:
    def __init__(self):
        self.client = storage.Client()
        self.bucket = self.client.bucket(settings.GCS_BUCKET_NAME)

    def upload_pdf(self, local_path, cloud_name):
        """Upload PDF para o Cloud Storage"""
        blob = self.bucket.blob(f"boletos/{cloud_name}")
        blob.upload_from_filename(local_path)

        # Define metadata
        blob.metadata = {
            "contentType": "application/pdf",
            "cacheControl": "private, max-age=0",
        }
        blob.patch()

        return blob.public_url

    def generate_signed_url(self, filename, expiration=15):
        """Gera URL temporária para download (15 minutos)"""
        blob = self.bucket.blob(f"boletos/{filename}")

        url = blob.generate_signed_url(
            version="v4", expiration=timedelta(minutes=expiration), method="GET"
        )

        return url

    def file_exists(self, filename):
        """Verifica se arquivo existe no bucket"""
        blob = self.bucket.blob(f"boletos/{filename}")
        return blob.exists()
