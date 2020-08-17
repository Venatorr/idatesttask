import os
from tempfile import NamedTemporaryFile
from urllib.request import urlopen
from django.core.files import File
from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Image(models.Model):
    name = models.TextField(verbose_name='Название')
    add_date = models.DateTimeField('added date', auto_now_add=True)
    image = models.ImageField(upload_to='images/', blank=True, null=False,
                              verbose_name='Изображение')
    image_url = models.URLField(blank=True, null=True,
                                verbose_name='Ссылка для изображений с внешних ресурсов')

    def save(self, *args, **kwargs):
        if self.image_url and not self.image:
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(urlopen(self.image_url).read())
            img_temp.flush()
            self.image.save(os.path.basename(self.image_url), File(img_temp), save=False)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-add_date', ]
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'
