"""Кэш Redis."""
import contextlib
import functools
import json
import os
from pathlib import Path
from typing import Dict

import redis  # Клиент для работы с Redis (база данных в памяти)
from dotenv import dotenv_values
from redis.backoff import (
    ExponentialBackoff,  # Алгоритм экспоненциального увеличения задержки между попытками
)
from redis.exceptions import ConnectionError, TimeoutError  # noqa: A004
from redis.retry import Retry  # Механизм повторных попыток при ошибках соединения

# В Redis может быть несколько "логических баз данных", нумеруются с 0.
# Мы просто задаём два индекса для разных целей (например, кэш и удалённые данные).
CACHE_DB: int = 0
REMOTE_DB: int = 1


def lazy_connect(db: int):
    """Декоратор, который лениво (по требованию) создаёт подключение к Redis для нужной базы. Если соединение для указанного db ещё не установлено, оно создаётся автоматически."""    
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Проверяем, есть ли уже соединение для этой базы
            keys = self.connections.keys()
            if db not in keys:
                # Если нет — создаём
                self.connections[db] = self.setup_connection(db=db)
            # Вызываем исходную функцию
            res = func(self, *args, **kwargs)
            return res
        return wrapper
    return decorator


class Cache:
    """Класс-обёртка для работы с Redis. Позволяет автоматически подключаться, хранить кэш и работать с удалёнными данными."""

    def __init__(self, envfile: str = '.env'):
        """Конструктор."""
        # Загружаем конфигурацию подключения из .env файла (например, REDIS_URL, REDIS_PORT и т.д.)
        self.config = {}
        if os.path.exists(envfile):  # noqa: PTH110
            self.config = dotenv_values(envfile)
        # Здесь будут храниться активные соединения к разным Redis DB (по номеру базы)
        self.connections: Dict[int, redis.Redis] = {}

    def setup_connection(self, db: int) -> redis.Redis:
        """Создаёт подключение к Redis для указанного номера базы данных. Настраивает автоматические повторы при ошибках соединения."""
        connection = redis.Redis(
            host=self.config['REDIS_URL'],  # Адрес Redis-сервера (например, localhost)
            port=self.config['REDIS_PORT'],  # Порт Redis (по умолчанию 6379)
            db=db,  # Номер базы данных (0, 1, 2 и т.д.)
            username=self.config['REDIS_USER'],  # Имя пользователя (если требуется)
            password=self.config['REDIS_USER_PASSWORD'],  # Пароль
            retry=Retry(ExponentialBackoff(cap=10, base=1), retries=25),  # Повторные попытки с увеличением задержки
            retry_on_error=[ConnectionError, TimeoutError, ConnectionResetError],  # Повторять при этих типах ошибок
            health_check_interval=1,  # Проверка 'живости' соединения каждые 1 секунду
        )
        return connection

    @lazy_connect(REMOTE_DB)
    def get(self, key, db=REMOTE_DB) -> str | None:        
        """Получает значение по ключу из Redis (удалённая база данных). Возвращает строку или None, если ключ не найден."""
        binary = self.connections[db].get(key)  # Получаем значение в виде байтов
        return binary.decode('utf-8') if binary is not None else None  # Декодируем в строку

    @lazy_connect(REMOTE_DB)
    def set(self, key, value, period, db=REMOTE_DB) -> None:
        """Сохраняет значение по ключу в Redis с возможностью указать срок жизни (TTL)."""
        self.connections[db].set(key, value)
        if isinstance(period, int) and period > 0:
            # Если задан положительный TTL — ключ удалится автоматически по истечении этого времени
            self.connections[db].expire(key, period)

    @lazy_connect(REMOTE_DB)
    def clear(self, key, db=REMOTE_DB) -> None:
        """Удаляет запись по ключу в Redis."""
        self.connections[db].delete(key)

    @lazy_connect(CACHE_DB)
    def cache_get(self, key) -> str | None:
        """Получает значение из локального кэша (база данных 0). Если Redis недоступен — возвращает None."""
        try:
            value = self.get(key=key, db=CACHE_DB)
        except ConnectionError:
            value = None
        return value

    @lazy_connect(CACHE_DB)
    def cache_set(self, key, value, period) -> None:
        """Сохраняет значение в локальном кэше. Если соединение с Redis прерывается — просто пропускаем (кэш не критичен)."""
        with contextlib.suppress(ConnectionError):
            self.set(key, value, period, db=CACHE_DB)

def cache_push(key,data,period):  
    """Отправить в кэш.""" 
    env_path = Path(__file__).parent.parent / '.env'
    cache = Cache(env_path)  
    cache_rows = []
    for row in data:
        cache_row = {k: f'{v}' for k, v in row.__dict__.items()}
        if cache_row not in cache_rows:
            cache_rows.append(cache_row)
    cache_json = json.dumps(cache_rows)
    cache.cache_set(key, cache_json, period)
    # print('Сохранили из Redis: '+ key + cache_json + ' в Redis (db=0)')

def cache_pull(key):   
    """Забрать из кэша."""
    env_path = Path(__file__).parent.parent / '.env'
    cache = Cache(env_path)  
    cache_json = cache.cache_get(key)
    # print('Прочитали из Redis: ', + key + cache_json)
    if cache_json is not None:
        return json.loads(cache_json)
    else:
        return []
    
def cache_clear(*keys):   
    """Очистить кэш."""
    env_path = Path(__file__).parent.parent / '.env'
    cache = Cache(env_path) 
    for key in keys: 
        cache.clear(key)
