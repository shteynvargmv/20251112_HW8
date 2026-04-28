"""Авторизация."""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from db.models import SCustom
from menus.quit import InputCancelled, is_quit


class Auth:
    """Авторизация."""
    def __init__(self, service):
        """Конструктор."""
        self.service = service

    def decorator(func):  # noqa: N805
        """Декоратор."""
        def wrapper(*arg):
            print('------------------------------------- Аутентификация -------------------------------------')
            func(*arg)
            print('------------------------------------------------------------------------------------------')
            print()
        return wrapper

    @decorator
    def display(self):
        """Отобразить меню авторизации."""
        scustom = self.user_input()
        if scustom is not None:
            print(f'Добро пожаловать, {scustom.name}!')                

    def user_input(self):
        """Пользовательский ввод."""
        user_phone = self.get_phone()
        #такой пользователь есть, возвращаем
        scustoms = self.service.get_scustom(('phone',), (user_phone,))
        if len(scustoms) > 0:
            count = 0
            while True:
                count += 1
                user_password = self.get_password()
                if user_password == scustoms[0].password:
                    return scustoms[0]
                elif count < 3:
                    print(f'Пароль неверный. Попытка: {count+1}')
                elif count == 3:
                    print('Пароль введен неверно 3 раза.')
                    raise InputCancelled()
        
        #такого нет, создаем и возвращаем
        user_name = self.get_name()
        user_password = self.get_password()
        self.service.add_scustom(SCustom(user_phone,user_name, user_password))         
        scustoms = self.service.get_scustom(('phone',), (user_phone,))       
        if len(scustoms) > 0:
            return scustoms[0]        
    
    def get_phone(self):
        """Ввод номера телефона."""
        while True:
            user_phone = input('Введите свой номер телефона: ')
            if not is_quit(user_phone):
                user_phone = user_phone.replace('-', '').replace(')', '').replace('(', '').replace(' ', '')
                if not user_phone.isdigit():
                    print('Введите числовое значение')
                else:
                    return user_phone
                
    def get_password(self):
        """Ввод пароля."""
        while True:
            user_password = input('Введите пароль: ')
            if not is_quit(user_password):
                if len (user_password) > 20:
                    print('Введите пароль не длиннее 20 символов')
                else:
                    return user_password
            
    def get_name(self):
        """Ввод имени."""
        while True:
            user_name = input('Введите свое имя: ')
            if not is_quit(user_name):
                return user_name.lower().capitalize()