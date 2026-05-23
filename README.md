# Сервис автоматизации закупок в розничной сети

Backend на Django REST Framework для заказа товаров через API.  
Реализована базовая и продвинутая часть дипломного проекта.

## Основные возможности

- Регистрация и авторизация (JWT-токены, подтверждение по email)
- Каталог товаров с категориями, поиском и сортировкой
- Корзина с товарами от разных поставщиков
- Оформление заказа с адресом доставки
- Отправка email-уведомлений клиенту и администратору (через Celery)
- Импорт товаров из YAML (через management-команду и Celery-задачу)
- Разграничение доступа: покупатель, поставщик, администратор
- Изменение статуса заказа поставщиком/администратором с уведомлением клиента
- Контейнеризация (Docker Compose)

## Стек

- Python 3.12, Django 5.1+, Django REST Framework
- Simple JWT для аутентификации
- Celery + Redis для асинхронных задач
- SQLite (для разработки)
- Docker, docker-compose
  
## Установка и запуск  
   
1. Клонирование репозитория и виртуальное окружение  
git clone <url-репозитория>  
cd diplom_netologia  
python -m venv venv  
source venv/bin/activate   # для Linux/MacOS  
pip install --upgrade pip  
pip install -r requirements.txt  
   
2. Настройка окружения  
Создайте файл .env в корне (или используйте переменные окружения):  
DEBUG=True  
SECRET_KEY=ваш-секретный-ключ  
ALLOWED_HOSTS=127.0.0.1,localhost  
   
Убедитесь, что в retail_service/settings.py для Celery указаны:  
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')  
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')  
   
3. Миграции и суперпользователь  
python manage.py migrate  
python manage.py createsuperuser  
   
4. Запуск Redis (необходим для Celery)  
sudo systemctl start redis    # или redis-server  
   
5. Запуск Celery worker (в отдельном терминале)  
celery -A retail_service worker -l info  
   
6. Запуск сервера разработки  
python manage.py runserver  
Приложение доступно по адресу http://127.0.0.1:8000/  
   
## Запуск через Docker Compose  
   
1. Убедитесь, что установлены Docker и docker-compose  
2. Из корня проекта выполните:  
docker-compose up --build  
Будут запущены сервисы:  
- web – Django (порт 8000)  
- redis – Redis (внутренняя сеть)  
- celery – Celery worker  
   
3. Создание суперпользователя внутри контейнера  
docker-compose exec web python manage.py createsuperuser  
   
4. Остановка  
Ctrl+C   # для graceful shutdown  
docker-compose down  
   
Импорт товаров  
   
Через management-команду (локально):  
python manage.py import_products data/shop1.yaml  
   
Через API (требуется аутентификация):  
Загрузите файл YAML, используя endpoint POST /api/v1/products/staff/import/  
Пример с curl (замените <токен> на JWT-токен администратора или поставщика):  
curl -X POST http://localhost:8000/api/v1/products/staff/import/ \  
  -H "Authorization: Bearer <токен>" \  
  -F "file=@data/shop1.yaml"  
Задача будет обработана асинхронно через Celery.  
   
## Основные API эндпоинты  
   
Аутентификация и пользователи  
POST /api/v1/accounts/register/ - Регистрация  
GET  /api/v1/accounts/confirm-email/<uidb64>/<token>/ - Подтверждение email  
POST /api/v1/accounts/token/ - Получение JWT-токена  
POST /api/v1/accounts/token/refresh/ - Обновление токена  
   
Товары и категории  
GET /api/v1/products/categories/ - Список категорий  
GET /api/v1/products/products/ - Список товаров  
GET /api/v1/products/products/<id>/ - Детали товара  
   
Корзина  
GET /api/v1/orders/cart/ - Просмотр корзины  
POST /api/v1/orders/cart/add/ - Добавление товара  
PATCH /api/v1/orders/cart/update/<id>/ - Изменение количества  
DELETE /api/v1/orders/cart/remove/<id>/ - Удаление товара  
   
Адреса доставки  
GET /api/v1/orders/addresses/ - Список адресов  
POST /api/v1/orders/addresses/ - Добавление адреса  
DELETE /api/v1/orders/addresses/<id>/ - Удаление адреса  
   
Заказы (покупатель)  
GET /api/v1/orders/orders/ - Список заказов  
GET /api/v1/orders/orders/<id>/ - Детали заказа  
POST /api/v1/orders/orders/create/ - Создание заказа из корзины  
   
Заказы (персонал: поставщик/админ)  
GET /api/v1/orders/staff/orders/ - Список заказов (поставщик видит только свои)  
PATCH /api/v1/orders/staff/orders/<id>/status/ - Изменение статуса заказа  
   
Структура проекта (основные компоненты)  
diplom_netologia/  
├── accounts/          # Пользователи, регистрация, аутентификация  
├── products/          # Категории, товары, ProductInfo, импорт  
├── orders/            # Корзина, заказы, адреса  
├── retail_service/    # Настройки Django, Celery, URL-маршруты  
├── data/              # YAML-файлы для импорта  
├── Dockerfile  
├── docker-compose.yml  
├── entrypoint.sh  
├── requirements.txt  
└── README.md  
   
## Переменные окружения  
DEBUG - Режим отладки Django - True  
SECRET_KEY - Секретный ключ Django - (обязательно)  
ALLOWED_HOSTS - Разрешённые хосты - *  
CELERY_BROKER_URL - URL брокера Celery - redis://localhost:6379/0  
CELERY_RESULT_BACKEND - Бэкенд результатов Celery - redis://localhost:6379/0  
   
