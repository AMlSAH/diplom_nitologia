from celery import shared_task
from .import_utils import process_yaml

@shared_task
def do_import(yaml_file_path):
    process_yaml(yaml_file_path)
    return f"Импорт из {yaml_file_path} завершён."
