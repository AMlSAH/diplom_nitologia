from django.core.management.base import BaseCommand
from products.import_utils import process_yaml


class Command(BaseCommand):
    help = 'Импорт товаров из YAML-файла в базу данных'

    def add_arguments(self, parser):
        parser.add_argument('yaml_file', type=str, help='Путь к YAML-файлу')

    def handle(self, *args, **options):
        yaml_file = options['yaml_file']
        process_yaml(yaml_file)
        self.stdout.write(self.style.SUCCESS('Импорт завершён.'))
