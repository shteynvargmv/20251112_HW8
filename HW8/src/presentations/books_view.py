"""Класс отображения бронирований."""
from tabulate import tabulate


class BooksView:
    """Класс отображения бронирований."""
    def __init__(self, sbooks_dto):
        """Конструктор."""
        self.sbooks_dto = sbooks_dto

    def display(self):
        """Отображение."""
        if not self.sbooks_dto:
            return
        
        out_data = []
        for dto in self.sbooks_dto:
            out_data.append([
                dto.bookid,
                dto.carrcode + dto.connid,            
                dto.fldate,
                dto.name
            ])
        
        headers = ['№', 'Рейс', 'Дата', 'Имя пассажира']
        print('')
        print(('Ваши бронирования:'))
        print(tabulate(out_data, headers=headers, tablefmt='grid'))
        print('')