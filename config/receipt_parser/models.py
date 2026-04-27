from django.db import models

class ReceiptView(models.Model):
    image = models.ImageField(upload_to='receipt_parser/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        fields = ", ".join(f"{f.name}={getattr(self, f.name)!r}" for f in self._meta.fields)
        return f"<{self.__class__.__name__} {fields}>"


class ItemCategories(models.Model):
    item_category_id = models.IntegerField(primary_key=True)
    item_category_name = models.CharField(max_length=100, unique=True, null=False)
    item_category_description = models.CharField(max_length=255, unique=False, null=True)
    item_categorie_insert_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        fields = ", ".join(f"{f.name}={getattr(self, f.name)!r}" for f in self._meta.fields)
        return f"<{self.__class__.__name__} {fields}>"

class StoreNames(models.Model):
    store_name_id = models.IntegerField(primary_key=True)
    store_name = models.CharField(max_length=100, unique=True, null=False)
    store_name_description = models.CharField(max_length=255, unique=False, null=True)
    store_name_insert_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        fields = ", ".join(f"{f.name}={getattr(self, f.name)!r}" for f in self._meta.fields)
        return f"<{self.__class__.__name__} {fields}>"

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
    item_insert_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        fields = ", ".join(f"{f.name}={getattr(self, f.name)!r}" for f in self._meta.fields)
        return f"<{self.__class__.__name__} {fields}>"


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
    store_insert_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        fields = ", ".join(f"{f.name}={getattr(self, f.name)!r}" for f in self._meta.fields)
        return f"<{self.__class__.__name__} {fields}>"


class PaymentMethods(models.Model):
    payment_method_id = models.IntegerField(primary_key=True)
    payment_method_name = models.CharField(max_length=100, unique=True, null=False)
    payment_method_description = models.CharField(max_length=255, unique=False, null=True)
    payment_method_insert_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        fields = ", ".join(f"{f.name}={getattr(self, f.name)!r}" for f in self._meta.fields)
        return f"<{self.__class__.__name__} {fields}>"


class ReceiptResources(models.Model):
    receipt_resource_id = models.IntegerField(primary_key=True)
    original_image_path = models.CharField(max_length=150, unique=True, null=False)
    grayscale_image_path = models.CharField(max_length=150, unique=True, null=True)
    visualization_image_path = models.CharField(max_length=150, unique=True, null=True)
    raw_text_json = models.CharField(max_length=150, unique=True, null=False)
    receipt_resource_insert_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        fields = ", ".join(f"{f.name}={getattr(self, f.name)!r}" for f in self._meta.fields)
        return f"<{self.__class__.__name__} {fields}>"


class Receipt(models.Model):
    receipt_id = models.IntegerField(primary_key=True)

    store_id_fk = models.ForeignKey(
        Stores,
        on_delete=models.DO_NOTHING,
        null=False,
        blank=False,
        related_name="stores_id_fk",
    )

    payment_method_id_fk = models.ForeignKey(
        PaymentMethods,
        on_delete=models.DO_NOTHING,
        null=False,
        blank=False,
        related_name="payment_methods_id_fk",
    )

    receipt_resource_id_fk = models.ForeignKey(
        ReceiptResources,
        on_delete=models.DO_NOTHING,
        null=False,
        blank=False,
        related_name="receipt_resources_id_fk",
    )

    receipt_datetime = models.DateTimeField(auto_now_add=False, null=False)
    receipt_insert_datetime = models.DateTimeField(auto_now_add=True)
    receipt_reference = models.CharField(max_length=100, unique=True, null=False)
    receipt_description = models.CharField(max_length=255, unique=False, null=True)

    def __str__(self):
        fields = ", ".join(f"{f.name}={getattr(self, f.name)!r}" for f in self._meta.fields)
        return f"<{self.__class__.__name__} {fields}>"

class ReceiptItems(models.Model):
    item_id_fk = models.ForeignKey(
        Items,
        on_delete=models.DO_NOTHING,
        null=False,
        blank=False,
        related_name="items_id_fk",
    )

    receipt_id_fk = models.ForeignKey(
        Receipt,
        on_delete=models.DO_NOTHING,
        null=False,
        blank=False,
        related_name="receipt_id_fk",
    )

    insert_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        fields = ", ".join(f"{f.name}={getattr(self, f.name)!r}" for f in self._meta.fields)
        return f"<{self.__class__.__name__} {fields}>"
