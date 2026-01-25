"""Тест бронирования."""
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from sqlalchemy.orm import sessionmaker

sys.path.append(str(Path(__file__).parent.parent.parent ))

from faker import Faker

from src.db.engine import Engine
from src.db.models import SAirport, SBook, SCarr, SCustom, SFlight, SPFli
from src.menus.booking import Booking
from src.menus.quit import InputCancelled
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

def test_create_sbook_valid_choice(session):
    """Тест: бронирование, выбран существующий рейс и мест для бронирования достаточно."""
    scustom = session.query(SCustom).first()
    if not scustom:
        scustom = SCustom(
                    phone = '89012345678',
                    name = 'User')
        session.add(scustom)
        session.commit()
    
    service = FlyService(session=session,customid=scustom.phone)
    booking = Booking(service)

    spfli, sflight, scarr = add_flight(session)

    sbook_before_booking = session.query(SBook).filter_by(
        carrid = spfli.carrid, 
        connid = spfli.connid, 
        fldate = sflight.fldate, 
        customid = scustom.phone).count()  

    with patch.object(booking, 'input_flight_param') as mock_flight_param, \
        patch.object(booking, 'input_flight') as mock_input_flight, \
        patch.object(booking, 'input_pass_count') as mock_input_pass_count, \
        patch('src.menus.booking.is_quit') as mock_is_quit, \
        patch('builtins.print') as mock_print:  
    
            mock_flight_param.return_value = {'cityfrom': f'{spfli.cityfrom}', 
                                            'cityto' : f'{spfli.cityto}',
                                            'fldate' : f'{sflight.fldate}'}
            flight = f'{scarr.carrcode}{sflight.connid} {sflight.fldate}'
            mock_input_flight.return_value = flight
            mock_input_pass_count.return_value = 1
            
            mock_is_quit.side_effect = is_quit_side_effect
            
            with pytest.raises(InputCancelled):
                booking.display()   

            mock_print.assert_called_with(f'Успешно забронировано: {flight}')  
    
    sbook_after_booking = session.query(SBook).filter_by(
        carrid = spfli.carrid, 
        connid = spfli.connid, 
        fldate = sflight.fldate, 
        customid = scustom.phone).count()
    
    assert sbook_after_booking - sbook_before_booking == 1 # noqa: S101

def test_create_sbook_invalid_choice(session):
    """Тест: бронирование, мест для бронирования нет."""
    scustom = session.query(SCustom).first()
    if not scustom:
        scustom = SCustom(
                    phone = '89012345678',
                    name = 'User')
        session.add(scustom)
        session.commit()
    
    service = FlyService(session=session,customid=scustom.phone)
    booking = Booking(service)

    spfli, sflight, scarr = add_flight(session)

    sbook_before_booking = session.query(SBook).filter_by(
        carrid = spfli.carrid, 
        connid = spfli.connid, 
        fldate = sflight.fldate, 
        customid = scustom.phone).count()  
    
    service.get_spfli_sflight(('spfli.cityfrom','spfli.cityto','sflight.fldate'), 
                        (spfli.cityfrom,spfli.cityto,sflight.fldate)) 

    with patch.object(booking, 'input_flight_param') as mock_flight_param, \
        patch.object(booking, 'input_flight') as mock_input_flight, \
        patch('src.menus.booking.is_quit') as mock_is_quit, \
        patch('src.menus.booking.prompt') as mock_prompt, \
        patch('builtins.print') as mock_print:
    
        mock_flight_param.return_value = {'cityfrom': f'{spfli.cityfrom}', 
                                        'cityto' : f'{spfli.cityto}',
                                        'fldate' : f'{sflight.fldate}'}
        flight = f'{scarr.carrcode}{sflight.connid} {sflight.fldate}'
        mock_input_flight.return_value = flight
        mock_prompt.side_effect = ['3','N'] #пытаемся бронировать 3, когда свободно 2
        mock_is_quit.side_effect = is_quit_side_effect
        
        with pytest.raises(InputCancelled):
            booking.display()  

        mock_print.assert_any_call('Для бронирования доступно только 2.')  

    sbook_after_booking = session.query(SBook).filter_by(
        carrid = spfli.carrid, 
        connid = spfli.connid, 
        fldate = sflight.fldate, 
        customid = scustom.phone).count()
    
    assert sbook_after_booking - sbook_before_booking == 0   # noqa: S101

def add_flight(session): 
    """Добавляем рейсы для бронирования."""
    faker = Faker()        
    sairports = list(session.query(SAirport).limit(2))
    if not sairports:
        name = faker.city()[:3].upper()
        sairport = SAirport(
                        id = 1, 
                        name = name, 
                        timezone = 'UTC-12')
        sairports.append(sairport)
        session.add(sairport)
        name = faker.city()[:3].upper()
        while name == SAirport.name:
            name = faker.city()[:3].upper()
        sairport = SAirport(
                        id = 2, 
                        name = name, 
                        timezone = 'UTC-12')
        sairports.append(sairport)
        session.add(sairport)
        session.commit()
    elif len(sairports) == 1:
        name = faker.city()[:3].upper()
        while name == sairports[0].name:
            name = faker.city()[:3].upper()
        sairport = SAirport(
                        id = sairports[0].id+1, 
                        name = name, 
                        timezone = 'UTC-12')
        sairports.append(sairport)
        session.add(sairport)
        session.commit()
    
    scarr = session.query(SCarr).first()
    if not scarr:
        carrname = faker.word().capitalize()
        scarr = SCarr(
                carrid = 1,
                carrname = carrname,
                carrcode = carrname[:2].upper(),
                url = faker.url())
        session.add(scarr)
        session.commit()
    
    spfli = session.query(SPFli).filter_by(airpfrom = sairports[0].id, airpto = sairports[1].id).first()
    if not spfli:
        spfli = SPFli(
                    carrid = scarr.carrid,
                    connid = faker.numerify(text='####'),
                    countryfr = faker.country(),
                    cityfrom = faker.city(),
                    airpfrom = sairports[0].id,
                    countryto = faker.country(),
                    cityto = faker.city(),
                    airpto = sairports[1].id,
                    fltime = faker.time())
        session.add(spfli)
        session.commit()
    sflight = session.query(SFlight).filter_by(carrid = spfli.carrid, connid = spfli.connid).first()
    if not sflight:
        sflight = SFlight(
                    carrid = spfli.carrid,
                    connid = spfli.connid,
                    fldate=faker.future_date(end_date='+365d'),
                    price=faker.pydecimal(left_digits=5,right_digits=2,positive=True,min_value=100,max_value=10000),
                    currency=faker.currency()[0],
                    planetype=faker.bothify(text='?').upper()+faker.numerify(text='###'),
                    seatsmax=4,
                    seatsocc=2)
        session.add(sflight)
        session.commit()
    else:
        sflight.seatsmax = 4
        sflight.seatsocc = 2
        session.commit()
    return spfli, sflight, scarr

def is_quit_side_effect(input_value):
    """Настраиваем is_quit."""
    if input_value == 'Q':
        raise InputCancelled()
    else:
        return False

