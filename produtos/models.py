from django.db import models
from io import BytesIO
from django.core.files.base import ContentFile, File
from django.conf import settings
from barcode import get_barcode_class
from barcode.writer import ImageWriter
from PIL import Image
import os
import logging

logger = logging.getLogger(__name__)

class Produto(models.Model):

    CATEGORIAS = [
        ('carnes', 'Carnes'),
        ('verduras', 'Verduras')
    ]

    FORMATOS = [
        ('code128', 'Code 128'),
        ('code39', 'Code 39'),
        ('ean13', 'EAN-13'),
        ('ean8', 'EAN-8'),
        ('upca', 'UPC-A'),
        ('jan', 'JAN'),
        ('isbn13', 'ISBN-13'),
        ('isbn10', 'ISBN-10'),
        ('issn', 'ISSN'),
        ('pzn', 'PZN'),
        ('ean14', 'EAN-14'),
        ('gs1_128', 'GS1-128'),
        ('itf', 'ITF'),
        ('codabar', 'Codabar'),
    ]

    nome = models.CharField(max_length=100)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    imagem = models.ImageField(upload_to='produtos/', blank=True)
    codigo = models.CharField(max_length=100, blank=True)
    formato = models.CharField(max_length=20, choices=FORMATOS, default="code128")
    barcode_image = models.ImageField(upload_to='barcodes/', blank=True, null=True)


    def __str__(self):
        return self.nome
    

    def save(self, *args, **kwargs):
        nome_slug = self.nome.lower().replace(" ", "_")
        formato_slug = self.formato.lower()

        # === Converte imagem enviada para WEBP ===
        if self.imagem and hasattr(self.imagem, 'file') and not self.imagem.name.endswith('.webp'):
            try:
                img = Image.open(self.imagem)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                buffer = BytesIO()
                img.save(buffer, format='WEBP', quality=80)
                buffer.seek(0)

                filename_webp = f"{nome_slug}_{formato_slug}.webp"
                self.imagem = ContentFile(buffer.getvalue(), name=filename_webp)

            except Exception as e:
                logger.error(f"Erro ao converter imagem de '{self.nome}': {e}")

        # === Usa imagem padrão sem conversão se nenhuma imagem foi enviada ===
        if not self.imagem:
            default_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'default_img.png')
            if os.path.exists(default_path):
                try:
                    with open(default_path, 'rb') as f:
                        filename = f"{nome_slug}_{formato_slug}.png"
                        self.imagem.save(filename, File(f), save=False)
                except Exception as e:
                    logger.error(f"Erro ao carregar imagem padrão para '{self.nome}': {e}")

        # Salva o objeto com a imagem final (webp ou padrão)
        super().save(*args, **kwargs)

        # === Geração do código de barras ===
        if self.codigo:
            filename_barcode = f"{nome_slug}_{formato_slug}.png"
            needs_gen = not self.barcode_image or settings.DEBUG

            if needs_gen:
                try:
                    barcode_class = get_barcode_class(self.formato)
                    barcode_obj = barcode_class(self.codigo, writer=ImageWriter())
                    buffer = BytesIO()
                    barcode_obj.write(buffer)
                    buffer.seek(0)

                    self.barcode_image.save(filename_barcode, ContentFile(buffer.getvalue()), save=False)
                    super().save(update_fields=['barcode_image'])
                except Exception as e:
                    logger.error(f"Erro ao gerar código de barras para '{self.nome}': {e}")
        else:
            if self.barcode_image:
                self.barcode_image.delete(save=False)
