import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from recipe.models import Ingredient

DATA_DIR = Path(settings.BASE_DIR) / 'data'
CSV_FILE = DATA_DIR / 'ingredients.csv'


class Command(BaseCommand):

    help = 'Импорт данных Ingredient.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('Начинаем импорт CSV...'))
        self.load_ingredient()
        self.stdout.write(self.style.SUCCESS('Импорт завершён успешно!'))

    def load_ingredient(self):
        file_path = DATA_DIR / 'ingredients.csv'
        if not file_path.exists():
            self.stdout.write(self.style.ERROR('ingredients.csv не найден'))
            return
        with file_path.open(encoding='utf-8') as f:
            for row in csv.DictReader(f):
                Ingredient.objects.get_or_create(
                    name=row['name'],
                    measurement_unit=row['measurement_unit']
                )
        self.stdout.write(self.style.SUCCESS('Ингредиенты загружены.'))
