import yaml
from accounts.models import Shop
from products.models import Category, Product, ProductInfo
from django.contrib.auth import get_user_model

User = get_user_model()

def process_yaml(yaml_file_path):
    with open(yaml_file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    if not isinstance(data, list):
        data = [data]

    for shop_data in data:
        _process_shop(shop_data)

def _process_shop(shop_data):
    shop_name = shop_data.get('shop')
    if not shop_name:
        raise ValueError('Поле "shop" обязательно')

    supplier_user = User.objects.filter(user_type='supplier').first()
    if not supplier_user:
        supplier_user = User.objects.create_user(
            email='importer@gmail.com',
            username='importer',
            password='123123',
            user_type='supplier'
        )

    shop, created = Shop.objects.get_or_create(
        name=shop_name,
        defaults={'user': supplier_user, 'url': shop_data.get('url', '')}
    )
    if not created:
        shop.url = shop_data.get('url', '')
        shop.save()

    cat_map = {}
    for cat_data in shop_data.get('categories', []):
        cat = _process_category(cat_data, cat_map)
        cat_map[cat_data['id']] = cat

    for good_data in shop_data.get('goods', []):
        _process_good(good_data, shop, cat_map)

def _process_category(cat_data, cat_map):
    name = cat_data['name']
    parent_id = cat_data.get('parent')
    parent = cat_map.get(parent_id) if parent_id else None

    category, _ = Category.objects.get_or_create(
        name=name,
        parent=parent
    )
    return category

def _process_good(good_data, shop, cat_map):
    external_id = good_data.get('id')
    if not external_id:
        return

    category_id = good_data.get('category')
    category = cat_map.get(category_id)
    if not category:
        return

    product, created = Product.objects.get_or_create(
        name=good_data['name'],
        defaults={'category': category}
    )
    if not created and product.category != category:
        product.category = category
        product.save()

    price = good_data.get('price', 0)
    quantity = good_data.get('quantity', 0)
    parameters = good_data.get('parameters', {})

    ProductInfo.objects.update_or_create(
        product=product,
        shop=shop,
        defaults={
            'external_id': external_id,
            'price': price,
            'quantity': quantity,
            'parameters': parameters
        }
    )
