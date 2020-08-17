import os
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from .models import Image
from .forms import ImageForm, ImageSizeForm
from PIL import Image as im
from idatesttask.settings import BASE_DIR
from tempfile import NamedTemporaryFile

IMAGES_ON_PAGE = 10


def index(request):
    images_list = Image.objects.all()
    paginator = Paginator(images_list, IMAGES_ON_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'paginator': paginator}
    return render(request, 'index.html', context)


def add_image(request):
    form = ImageForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('index')
    context = {'form': form}
    return render(request, 'adding_image.html', context)


def get_resized_image(image, w, h):
    image_file = im.open(image.image)
    old_w, old_h = image_file.size
    # Корректный размер по-хорошему должен задаваться на фронте,
    # здесь упрощенная обработка при условии, что на фронте провести проверку нельзя
    # также проще было бы сделать через метод thumbnail, но в ТЗ не было
    # ограничения, что нельзя увеличивать изображение
    if old_w != w:
        wpercent = (w / float(old_w))
        new_h = int((float(old_h) * float(wpercent)))
        image_file = image_file.resize((w, new_h), im.ANTIALIAS)
    else:
        hpercent = (h / float(old_h))
        new_w = int((float(old_w) * float(hpercent)))
        image_file = image_file.resize((new_w, h), im.ANTIALIAS)
    return image_file


def set_image(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    if request.method == 'POST':
        form = ImageSizeForm(request.POST)
        if form.is_valid():
            image_file = get_resized_image(
                image, int(form.cleaned_data['width']), int(form.cleaned_data['height']))
            name, ext = os.path.splitext(image.image.url)
            new_w, new_h = image_file.size
            relative_path_name = name + '_' + str(new_w) + 'x' + str(new_h) + ext
            absolute_path_name = str(BASE_DIR) + relative_path_name
            if not os.path.isfile(absolute_path_name):
                image_file.save(absolute_path_name)
                f = open(absolute_path_name, 'rb')
                img_temp = NamedTemporaryFile(delete=True)
                img_temp.write(f.read())
                img_temp.flush()
                image.image.save(os.path.basename(relative_path_name), img_temp, save=True)
        else:
            context = {'image': image, 'form': form}
            return render(request, 'image_settings.html', context)
    data = {'width': image.image.width,
            'height': image.image.height}
    form = ImageSizeForm(initial=data)
    context = {'image': image, 'form': form}
    return render(request, 'image_settings.html', context)
