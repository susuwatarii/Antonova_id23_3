from celery import Celery  # Библиотека для запуска фоновых задач (asynchronous tasks)
from redislite.client import Redis
from dotenv import load_dotenv
import os


load_dotenv()
socket_path = os.getenv('REDIS_SOCKET_PATH', '/tmp/redis.sock')
redis_path = os.getenv('REDIS_DB_PATH', 'redis.db')

redis = Redis(redis_path, unix_socket_path=socket_path)  #  запускает встроенный Redis-сервер, Фиксированный путь к сокету
redis.flushall()  # Очищаем от задач оставшихся с прошлого раза, не использовать в проде

celery_app = Celery(
    'worker',  # Просто имя приложения Celery
    broker=f'redis+socket:///{socket_path}?db=0',
    backend=f'redis+socket:///{socket_path}?db=1',
)

celery_app.conf.task_track_started = True  # Celery будет явно ставить состояние STARTED, а не прыгать с PENDING в SUCCESS
celery_app.conf.result_expires = 3600  # Результат задачи будет храниться час
