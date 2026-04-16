from django.db import models

class Receipt(models.Model):
    image = models.ImageField(upload_to='receipt_parser/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
