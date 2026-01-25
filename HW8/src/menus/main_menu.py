"""Главное меню."""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent ))
from menus.auth import Auth
from menus.booking import Booking


class MainMenu:
    """Главное меню."""
    def __init__(self, service):
        """Конструктор."""
        self.service = service

    def decorator(func):  # noqa: N805
        """Декоратор."""
        def wrapper(*arg):
            print('******************************************************************************************')
            print('*--------------- Система бронирования авиабилетов (для выхода введите Q) ----------------*')
            print('******************************************************************************************')
            print()
            func(*arg)        
        return wrapper

    @decorator
    def display(self):
        """Отобразить главное меню."""
        Auth(self.service).display() 
        Booking(self.service).display()        

