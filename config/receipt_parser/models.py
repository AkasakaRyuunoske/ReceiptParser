from django.db import models

class ReceiptView(models.Model):
    image = models.ImageField(upload_to='receipt_parser/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

# class Receipt(models.Model):
#     receipt_id = models.IntegerField(primary_key=True)
#     receipt_reference = models.CharField(max_length=100, unique=True, null=False)

class ItemCategories(models.Model):
    item_category_id = models.IntegerField(primary_key=True)
    item_category_name = models.CharField(max_length=100, unique=True, null=False)
    item_category_description = models.CharField(max_length=255, unique=False, null=True)
    item_categories_insert_datetime = models.DateTimeField(auto_now_add=True)

class StoreNames(models.Model):
    store_name_id = models.IntegerField(primary_key=True)
    store_name = models.CharField(max_length=100, unique=True, null=False)
    store_name_description = models.CharField(max_length=255, unique=False, null=True)
    store_names_insert_datetime = models.DateTimeField(auto_now_add=True)

class Items(models.Model):
    item_id = models.IntegerField(primary_key=True)
    category_id_fk = models.ForeignKey(
        ItemCategories,
        on_delete=models.DO_NOTHING,
        null=False,
        blank=False,
        related_name="items_category_id_fk",
    )
    item_name = models.CharField(max_length=100, unique=True, null=False)
    price = models.IntegerField(null=False)
    item_description = models.CharField(max_length=255, unique=False, null=True)
    items_insert_datetime = models.DateTimeField(auto_now_add=True)

class Stores(models.Model):
    store_id = models.IntegerField(primary_key=True)
    store_name_id_fk = models.ForeignKey(
        StoreNames,
        on_delete=models.DO_NOTHING,
        null=False,
        blank=False,
        related_name="stores_name_id_fk",
    )
    address = models.CharField(max_length=100, unique=False, null=False)
    city = models.CharField(max_length=100, unique=True, null=False)
    stores_insert_datetime = models.DateTimeField(auto_now_add=True)
