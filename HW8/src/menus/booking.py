"""Бронирование."""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
import re
from datetime import datetime
from typing import List

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

from menus.quit import is_quit
from presentations.fly_view import FlyView


class Booking:
    """Бронирование."""
    def __init__(self, service):
        """Конструктор."""
        self.service = service

    def decorator(func):  # noqa: N805
        """Декоратор."""
        def wrapper(*arg):
            print('-------------------------------------- Выбор рейсов -------------------------------------')
            func(*arg)
            print('-----------------------------------------------------------------------------------------')
        return wrapper

    @decorator
    def display(self):
        """Отобразить меню бронирования."""
        success = False
        while not success:
            print('')
            flight = self.flight_choice()  
            if flight and len(flight) > 0:   
                res = self.booking(flight)
                if len(res) > 0:
                    print(f'Успешно забронировано: {flight}')
                    success = bool(not is_quit('Q'))
            else:
                success = bool(not is_quit('Q'))


    def input_flight_param(self):
        """Ввод параметров перелета."""
        spflies = self.service.get_spfli()
        cityfrom = self.input_cityfrom(spflies)
        cityto = self.input_cityto(spflies)
        sflights = []
        for fly in list(filter( lambda dto: dto.cityfrom == cityfrom and dto.cityto == cityto, spflies)):
            sflights += self.service.get_sflight(('mandt','carrid','connid'),(fly.mandt,fly.carrid,fly.connid))

        fldate = self.input_fldate(sflights)
        return {'cityfrom': cityfrom, 'cityto' : cityto, 'fldate' : fldate}      
    
    def input_cityfrom(self, spflies):
        """Ввод города отправления."""
        while True:            
            citiesfrom = []
            for spfli in spflies:
                if spfli.cityfrom not in citiesfrom:
                    citiesfrom.append(spfli.cityfrom)
            completer = WordCompleter(citiesfrom)
            cityfrom = prompt('Город отправления (Tab+↑↓): ', complete_while_typing=True, completer=completer)
            if not is_quit(cityfrom):
                if cityfrom in citiesfrom:
                    return cityfrom
                else:
                    print('Выберите город из списка')

    def input_cityto(self, spflies):
        """Ввод города прибытия."""
        while True:            
            citiesto = []
            for spfli in spflies:
                if spfli.cityto not in citiesto:
                    citiesto.append(spfli.cityto)
            completer = WordCompleter(citiesto)
            cityto = prompt('Город прибытия (Tab+↑↓): ', complete_while_typing=True, completer=completer)
            if not is_quit(cityto):
                if cityto in citiesto:
                    return cityto
                else:
                    print('Выберите город из списка')

    def input_fldate(self,spflies):
        """Ввод даты перелета."""
        while True:
            fldates = []
            for spfli in spflies:
                date = spfli.fldate.strftime('%d.%m.%Y')
                if date not in fldates:
                    fldates.append(date)
            completer = WordCompleter(fldates)
            fldate = prompt('Введите дату (ДД.ММ.ГГГГ): ', complete_while_typing=True, completer=completer)
            if not is_quit(fldate):
                pattern = r'^\d{2}\.\d{2}\.\d{4}$'
                if not re.match(pattern, fldate):
                    print('Используйте формат ДД.ММ.ГГГГ (например: 01.01.2026)')
                else:
                    try:
                        day, month, year = map(int, fldate.split('.'))
                        fldate = datetime(year, month, day)
                        if fldate < datetime.now():
                            print('Выберите дату в будущем')
                        else:
                            return fldate.date()
                    except ValueError:
                        print('Некорректная дата')

    def input_flight(self,fly_dtos):
        """Ввод рейса."""
        if fly_dtos:
            while True:            
                flights = []
                for fly_dto in fly_dtos:
                    flights.append(f'{fly_dto.carrcode}{fly_dto.connid} {fly_dto.fldate}')
                completer = WordCompleter(flights)
                flight = prompt('Выберите рейс (Tab+↑↓): ', completer=completer)
                if not is_quit(flight):
                    if flight in flights:
                        return flight
                    else:
                        print('Выберите рейс из списка')

    def input_pass_count(self, seatsfree):
        """Ввод количества пассажиров."""
        while True:
            pass_count = prompt(f'Введите количество пассажиров (max: {seatsfree}): ')
            if not is_quit(pass_count):
                if not pass_count.isdigit() or int(pass_count) < 0:
                    print('Введите числовое значение > 0')
                else:
                    pass_count = int(pass_count)
                    if pass_count > seatsfree: 
                        return 0                       
                    else:
                        return int(pass_count)                

    def flight_choice(self):
        """Вывод рейса."""
        values = self.input_flight_param()
        fly_dtos = self.service.get_spfli_sflight(('spfli.cityfrom','spfli.cityto','sflight.fldate'), 
                                                (values['cityfrom'],values['cityto'],values['fldate'])) 
        fly_dtos = list(filter( lambda dto: dto.seatsfree > 0, fly_dtos))       
        FlyView(fly_dtos).display()     
        return self.input_flight(fly_dtos)
    
    def booking(self, flight, pass_count = None) -> List[int]:
        """Бронирование."""
        if flight and len(flight) == 17: 
            res = []
            cache = self.service.get_cache_spfli_sflight()
            dtos = list(filter( lambda dto: dto.carrcode == flight[0:2] and dto.connid == flight[2:6] and dto.fldate == flight[7:17], 
                                cache))
            if len(dtos) > 0:
                dto = dtos[0]
                seatsfree = int(dto.seatsmax) - int(dto.seatsocc)
                if not pass_count:
                    pass_count = 0
                    pass_count = self.input_pass_count(seatsfree)
                
                if pass_count > 0:
                    dto.seatsocc = int(dto.seatsocc) + pass_count
                    self.service.update_sflight(dto)
                    res = self.service.update_sbook(dto,pass_count)

                    for c in cache: 
                        if c.mandt == dto.mandt and c.carrid == dto.carrid and \
                            c.connid == dto.connid and c.fldate == dto.fldate:
                            c = dto
                        c = dto   
                    self.service.set_cache_spfli_sflight(cache)
                    return res
                else:
                    while True:
                        print(f'Для бронирования доступно только {seatsfree}.')
                        des = prompt('Выбрать другой рейс? (Y/N):')   
                        if not is_quit(des):
                            if des.upper() == 'Y':
                                return res
                            elif des.upper() == 'N':  
                                is_quit('Q') 





