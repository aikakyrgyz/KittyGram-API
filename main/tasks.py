# tasks.py

from time import sleep
from celery import shared_task
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request

from .models import CatImages

# activate celery: rabbitmq-server

'''run commands in separate terminals:


celery -A kittygram beat -l info
celery -A kittygram  worker -l info
python manage.py runserver


'''

@shared_task
# do some heavy stuff
def crawl_images():
    print('Crawling data and creating objects in database ..')
    req = Request('https://ohcat.ru/gallery.html', headers={'User-Agent': 'Mozilla/5.0'})
    html = urlopen(req).read()
    bs = BeautifulSoup(html, 'html.parser')
    all_pics = bs.find('div', class_="text-center mt-3").find_all('a')
    for pic in all_pics:
        image = pic.get('href')
        print({'image': image})
        CatImages.objects.create(image_url=image)
        sleep(3)

@shared_task
def update_images():
    print('Updating data ..')
    req = Request('https://ohcat.ru/gallery.html', headers={'User-Agent': 'Mozilla/5.0'})
    html = urlopen(req).read()
    bs = BeautifulSoup(html, 'html.parser')
    all_pics = bs.find('div', class_="text-center mt-3").find_all('a')
    for pic in all_pics:
        image = pic.get('href')
        print({'image': image})
        data = {'image_url': image}
        CatImages.objects.filter(image_url=image).update(**data)
        sleep(3)
# Run this function if database is empty
if not CatImages.objects.all():
    crawl_images()

while True:
    sleep(15)
    update_images()