"""Класс отображения рейсов."""
from tabulate import tabulate


class FlyView:
    """Класс отображения рейсов."""
    def __init__(self, fly_dtos):
        """Конструктор."""
        self.fly_dtos = fly_dtos

    def display(self):
        """Отображение."""
        if not self.fly_dtos:
            print('Рейсы не найдены.')
            return
        
        out_data = []
        for dto in self.fly_dtos:
            out_data.append([
                dto.carrcode + dto.connid,
                dto.countryfr + ', ' + dto.cityfrom, 
                dto.countryto + ', ' + dto.cityto,               
                dto.fltime,
                dto.fldate,
                dto.price,
                dto.currency,
                dto.planetype
            ])
        
        headers = ['Рейс', 'Откуда', 'Куда', 'Время', 'Дата', 'Цена', 'Валюта', 'Самолет']
        print(('Список рейсов:'))
        print(tabulate(out_data, headers=headers, tablefmt='grid'))