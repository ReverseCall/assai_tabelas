from django.core.files.base import ContentFile, File
from barcode.writer import ImageWriter
from barcode import get_barcode_class
from django.conf import settings
from django.db import models
from io import BytesIO
from PIL import Image
import logging
import os

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
    codigo = models.CharField(max_length=100, blank=False)
    formato = models.CharField(max_length=20, choices=FORMATOS, default="code128")
    barcode_image = models.ImageField(upload_to='barcodes/', blank=True, null=True)

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        nome_slug = self.nome.lower().replace(" ", "_")
        formato_slug = self.formato.lower()
        filename_img = f"{nome_slug}_{formato_slug}.webp"
        filename_barcode = f"{nome_slug}_{formato_slug}.png"

        # Verifica se é update (já existe no banco)
        if self.pk:
            old = Produto.objects.filter(pk=self.pk).first()
            if old:
                old_nome_slug = old.nome.lower().replace(" ", "_")
                old_formato_slug = old.formato.lower()
                old_filename_img = f"{old_nome_slug}_{old_formato_slug}.webp"
                old_filename_barcode = f"{old_nome_slug}_{old_formato_slug}.png"

                # === Renomeia imagem se nome ou formato mudou ===
                if (old.nome != self.nome or old.formato != self.formato) and old.imagem:
                    old_img_path = os.path.join(settings.MEDIA_ROOT, 'produtos', old_filename_img)
                    new_img_path = os.path.join(settings.MEDIA_ROOT, 'produtos', filename_img)

                    if os.path.exists(old_img_path) and not os.path.exists(new_img_path):
                        os.rename(old_img_path, new_img_path)
                        self.imagem.name = os.path.join('produtos', filename_img)

                # === Renomeia código de barras se necessário ===
                if (old.nome != self.nome or old.formato != self.formato) and old.barcode_image:
                    old_barcode_path = os.path.join(settings.MEDIA_ROOT, 'barcodes', old_filename_barcode)
                    new_barcode_path = os.path.join(settings.MEDIA_ROOT, 'barcodes', filename_barcode)

                    if os.path.exists(old_barcode_path) and not os.path.exists(new_barcode_path):
                        os.rename(old_barcode_path, new_barcode_path)
                        self.barcode_image.name = os.path.join('barcodes', filename_barcode)

        # === Converter imagem enviada para WEBP ===
        if self.imagem and hasattr(self.imagem, 'file') and not self.imagem.name.endswith('.webp'):
            try:
                img = Image.open(self.imagem)
                if img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGBA' if 'A' in img.getbands() else 'RGB')

                buffer = BytesIO()
                if img.mode == 'RGBA':
                    img.save(buffer, format='WEBP', lossless=True)
                else:
                    img.save(buffer, format='WEBP', quality=80)

                buffer.seek(0)
                self.imagem = ContentFile(buffer.getvalue(), name=filename_img)
            except Exception as e:
                logger.error(f"Erro ao converter imagem: {e}")

        # === Imagem padrão se nenhuma enviada ===
        if not self.imagem:
            default_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'default_img.png')
            if os.path.exists(default_path):
                with open(default_path, 'rb') as f:
                    self.imagem.save(filename_img, File(f), save=False)

        # Primeiro salva com imagem (convertida ou padrão)
        super().save(*args, **kwargs)

        # === Gerar código de barras ===
        barcode_path = os.path.join(settings.MEDIA_ROOT, 'barcodes', filename_barcode)
        if self.codigo:
            if not os.path.exists(barcode_path):
                try:
                    barcode_class = get_barcode_class(self.formato)
                    barcode_obj = barcode_class(self.codigo, writer=ImageWriter())
                    buffer = BytesIO()
                    barcode_obj.write(buffer)
                    buffer.seek(0)
                    self.barcode_image.save(filename_barcode, ContentFile(buffer.getvalue()), save=False)
                    super().save(update_fields=['barcode_image'])
                except Exception as e:
                    logger.error(f"Erro ao gerar código de barras: {e}")
            else:
                self.barcode_image.name = os.path.join('barcodes', filename_barcode)
                super().save(update_fields=['barcode_image'])
