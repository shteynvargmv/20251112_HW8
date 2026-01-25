"""Тест авторизации."""
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from sqlalchemy.orm import sessionmaker

sys.path.append(str(Path(__file__).parent.parent.parent ))
from faker import Faker

from src.db.engine import Engine
from src.db.models import SCustom
from src.menus.auth import Auth
from src.services.fly_service import FlyService


@pytest.fixture(scope='session')
def connection():
    """Одна сессия соединения для всей сессии pytest."""
    connection = Engine().get_engine().connect()
    yield connection
    connection.close()

@pytest.fixture()  # noqa: PT001
def session(connection):
    """Начинаем транзакцию."""
    transaction = connection.begin()
    session_f = sessionmaker(bind=connection)
    session = session_f()

    yield session  # Тест использует session

    # Откатываем все изменения после теста
    session.close()
    transaction.rollback()

def test_auth_user_exists(session):
    """Тест: авторизация, пользователь существует в БД."""
    scustom = session.query(SCustom).first()
    if not scustom:
        scustom = SCustom(
                    phone = '89012345678',
                    name = 'User')
        session.add(scustom)
        session.commit()
    
    service = FlyService(session=session,customid=scustom.phone)
    auth = Auth(service)

    with patch('builtins.input') as mock_input, \
        patch('builtins.print') as mock_print:  
        
        mock_input.return_value = scustom.phone
        auth.display()
        mock_print.assert_any_call(f'Добро пожаловать, {scustom.name}!')  

def test_auth_user_does_not_exist(session):
    """Тест: авторизация, пользователь не существует в БД, создается."""
    faker = Faker()
    name = 'Username'
    phone = faker.numerify(text='###########')
    scustom = session.query(SCustom).filter_by(phone=phone).first()
    while scustom:
        phone = faker.numerify(text='###########')
        scustom = session.query(SCustom).filter_by(phone=phone).first()
    
    service = FlyService(session=session,customid=phone)
    auth = Auth(service)

    with patch('builtins.input') as mock_input, \
        patch('builtins.print') as mock_print:
    
        mock_input.side_effect = [phone,name]
        auth.display() 

        assert session.query(SCustom).filter_by(phone=phone).count() == 1  # noqa: S101

        mock_print.assert_any_call(f'Добро пожаловать, {name}!')  

