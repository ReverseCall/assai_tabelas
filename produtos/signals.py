from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import Produto
import os
import shutil

@receiver(post_delete, sender=Produto)
def deletar_arquivos_produto(sender, instance, **kwargs):
    if instance.imagem and instance.imagem.path:
        instance.imagem.delete(False)
    if instance.barcode_image and instance.barcode_image.path:
        instance.barcode_image.delete(False)
