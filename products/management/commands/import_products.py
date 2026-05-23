import yaml
from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import Shop
from products.models import Category, Product, ProductInfo
from products.import_utils import process_yaml


class Command(BaseCommand):
    help = 'Импорт товаров из YAML-файла в базу данных'

    def add_arguments(self, parser):
        parser.add_argument('yaml_file', type=str, help='Путь к YAML-файлу')

    def handle(self, *args, **options):
        yaml_file = options['yaml_file']
        process_yaml(yaml_file)

        self.stdout.write(self.style.SUCCESS('Импорт завершён.'))

        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        if not isinstance(data, list):
            data = [data]

        for shop_data in data:
            self._process_shop(shop_data)

        self.stdout.write(self.style.SUCCESS('Импорт завершён.'))

    def _process_shop(self, shop_data):
        shop_name = shop_data.get('shop')
        if not shop_name:
            self.stdout.write(self.style.ERROR('Поле "shop" обязательно'))
            return

        default_user = None
        from django.contrib.auth import get_user_model
        User = get_user_model()

        supplier_user = User.objects.filter(user_type='supplier').first()
        if not supplier_user:
            self.stdout.write(self.style.WARNING(
                'Нет пользователя-поставщика. Создаётся системный пользователь "importer".'
            ))
            supplier_user = User.objects.create_user(
                email='importer@example.com',
                username='importer',
                password='importer123',
                user_type='supplier'
            )

        shop, created = Shop.objects.get_or_create(
            name=shop_name,
            defaults={'user': supplier_user, 'url': shop_data.get('url', '')}
        )
        if created:
            self.stdout.write(f'Создан магазин: {shop_name}')
        else:
            shop.url = shop_data.get('url', '')
            shop.save()

        cat_map = {}
        for cat_data in shop_data.get('categories', []):
            cat = self._process_category(cat_data, cat_map)
            cat_map[cat_data['id']] = cat

        for good_data in shop_data.get('goods', []):
            self._process_good(good_data, shop, cat_map)

    def _process_category(self, cat_data, cat_map):
        cat_id = cat_data['id']
        name = cat_data['name']
        parent_id = cat_data.get('parent')
        parent = cat_map.get(parent_id) if parent_id else None


        category, created = Category.objects.get_or_create(
            name=name,
            parent=parent
        )
        return category

    def _process_good(self, good_data, shop, cat_map):
        external_id = good_data.get('id')
        if not external_id:
            self.stdout.write(self.style.WARNING('Товар без id пропущен'))
            return

        category_id = good_data.get('category')
        category = cat_map.get(category_id)
        if not category:
            self.stdout.write(self.style.WARNING(
                f'Категория с id {category_id} не найдена для товара {external_id}'
            ))
            return

        product, created = Product.objects.get_or_create(
            name=good_data['name'],
            defaults={
                'category': category,
                'description': '',
            }
        )
        if not created and product.category != category:
            product.category = category
            product.save()

        price = good_data.get('price', 0)
        quantity = good_data.get('quantity', 0)
        parameters = good_data.get('parameters', {})

        product_info, info_created = ProductInfo.objects.get_or_create(
            product=product,
            shop=shop,
            defaults={
                'external_id': external_id,
                'price': price,
                'quantity': quantity,
                'parameters': parameters
            }
        )

        if not info_created:
            product_info.external_id = external_id
            product_info.price = price
            product_info.quantity = quantity
            product_info.parameters = parameters
            product_info.save()
