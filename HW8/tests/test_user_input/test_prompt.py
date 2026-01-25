"""Тест пользовательского ввода."""
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

sys.path.append(str(Path(__file__).parent.parent.parent ))
from src.menus.booking import Booking
from src.menus.quit import InputCancelled

# def booking():    
#     from src.menus.booking import Booking
#     return Booking

def create_spflies(cities):
    """Фиктивные данные."""
    spflies = []
    for city in cities:
        spfli = Mock()
        spfli.cityfrom = city
        spflies.append(spfli)
    return spflies

class TestInputCityFrom:   
    """Класс теста.""" 
    def setup_method(self):
        """Настройка."""
        self.mock_service = Mock()
        self.booking = Booking(self.mock_service)
    
    def test_valid_cityfrom(self):
        """Тест: выбор существующего города из списка."""
        spflies = create_spflies(['Moscow', 'Perm', 'Rome'])
        
        # Mock зависимостей
        with patch('src.menus.booking.is_quit') as mock_is_quit, \
            patch('src.menus.booking.prompt') as mock_prompt:
            
            mock_is_quit.return_value = False
            mock_prompt.return_value = 'Perm'
            
            result = self.booking.input_cityfrom(spflies)
            
            assert result == 'Perm'  # noqa: S101
            mock_is_quit.assert_called_once_with('Perm')
    
    def test_invalid_cityfrom_then_quit(self):
        """Тест: неверный город, затем выход."""
        spflies = create_spflies(['Moscow', 'Rome'])
        
        with patch('src.menus.booking.prompt') as mock_prompt, \
            patch('src.menus.booking.is_quit') as mock_is_quit, \
            patch('builtins.print') as mock_print, \
            patch('src.menus.quit.confirm_exit') as mock_confirm_exit:
            
            mock_prompt.side_effect = ['Perm', 'Q']
            
            def is_quit_side_effect(input_value):
                if input_value == 'Perm':
                    return False
                elif input_value == 'Q':
                    if mock_confirm_exit.return_value:
                        raise InputCancelled()
                    return True
            
            mock_is_quit.side_effect = is_quit_side_effect
            mock_confirm_exit.return_value = True  
            
            with pytest.raises(InputCancelled) as exc_info:
                self.booking.input_cityfrom(spflies)
            
            assert str(exc_info.value) == 'Операция отменена пользователем' # noqa: S101
            mock_print.assert_called_with('Выберите город из списка')
    
    def test_quit_command(self):
        """Тест выхода."""
        with patch('src.menus.booking.prompt') as mock_prompt, \
            patch('src.menus.booking.is_quit') as mock_is_quit, \
            patch('src.menus.quit.confirm_exit') as mock_confirm_exit:

            def is_quit_side_effect(input_value):  # noqa: ARG001
                if mock_confirm_exit.return_value:
                    raise InputCancelled()
                return True
            
            mock_is_quit.side_effect = is_quit_side_effect            

            mock_prompt.return_value = 'Q'
            mock_confirm_exit.return_value = True
            
            with pytest.raises(InputCancelled) as exc_info:
                self.booking.input_cityfrom([])

            assert str(exc_info.value) == 'Операция отменена пользователем' # noqa: S101