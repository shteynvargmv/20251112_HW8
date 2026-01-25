"""Для выхода по Q в любой момент работы приложения."""
class InputCancelled(Exception):  # noqa: N818
    """Исключение."""
    def __init__(self, message='Операция отменена пользователем'):
        """Конструктор."""
        self.message = message
        
    def __str__(self):
        """Вывод."""
        return self.message

def is_quit(user_input):
    """Проверка ввода."""
    if user_input.upper() == 'Q':
        if confirm_exit():
            raise InputCancelled()
        return True
    else:
        return False
        
def confirm_exit():
    """Подтверждение выхода."""
    while True:
        answer = input('Вы хотите выйти? (Y/N): ')
        if answer.upper() == 'Y':
            return True
        elif answer.upper() == 'N':
            return False