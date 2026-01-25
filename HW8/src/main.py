"""Система бронирования авиабилетов."""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from menus.main_menu import MainMenu
from menus.quit import InputCancelled
from presentations.books_view import BooksView
from services.fly_service import FlyService

service = FlyService()

def main():  
    """Главная функция."""      
    try:
        main_menu()
        book_disp() 
    finally:
        service.close()  

def main_menu():
    """Запуск главного меню."""
    try:
        # service.generate(10)
        # service.print_all() 
        MainMenu(service).display()

    except InputCancelled:        
        print('Всего доброго!')
    except Exception as e:
        print(e)

def book_disp():
    """Отобразить бронирования пользователя."""
    BooksView(service.get_bookings()).display() 

if __name__ == '__main__':
    main()