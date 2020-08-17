from django.forms import (ModelForm, TextInput, URLInput,
                          Form, CharField, ValidationError)
from .models import Image
import mimetypes
import os

MAX_IMAGE_SIZE = 1000


class ImageForm(ModelForm):
    class Meta:
        model = Image
        fields = ['name', 'image_url', 'image']
        widgets = {'name': TextInput, 'image_url': URLInput}
        help_texts = {
            'name': 'Укажите название изображения',
            'image_url': 'Укажите ссылку на изображение',
            'image': 'Или выберите изображение',
        }

    def clean(self):
        data = super().clean()
        image_url = data.get('image_url')
        image = data.get('image')
        if image and image_url:
            raise ValidationError('URL и изображение не могут быть выбраны одновременно')
        if not image and not image_url:
            raise ValidationError('Необходимо указать URL или выбрать изображение')
        if image_url:
            _, ext = os.path.splitext(image_url)
            if not ext:
                raise ValidationError('Неверный URL, отсутствует расширение у файла')
            if mimetypes.types_map[ext].split('/')[0] != 'image':
                raise ValidationError('Неверный URL, изображения с таким '
                                      'расширением не обрабтываются')
        return data


def validate_size(value):
    if not value.isdigit():
        raise ValidationError(f'Размер должен быть числом')
    value = int(value)
    if value <= 0 or value >= MAX_IMAGE_SIZE:
        raise ValidationError(f'Указан неверный размер изображения, '
                              f'должен быть > 0 и < {MAX_IMAGE_SIZE}')


class ImageSizeForm(Form):
    width = CharField(required=True, label='Ширина', validators=[validate_size])
    height = CharField(required=True, label='Высота', validators=[validate_size])
