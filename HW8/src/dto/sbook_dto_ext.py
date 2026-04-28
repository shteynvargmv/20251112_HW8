"""DTO для бронирований."""
from datetime import datetime


class SBookDTOExt:
    """DTO для бронирований."""
    def __init__(self,row):
        """Конструктор."""
        self.bookid = row.bookid
        self.carrcode = row.carrcode
        self.connid = row.connid
        if isinstance(row.fldate, str):
            year, month, day  = map(int, row.fldate.split('-'))
            self.fldate = datetime(year, month, day).date()
        else:
            self.fldate = row.fldate
        self.carrname = row.carrname
        self.cityfrom = row.cityfrom
        self.airpfrom = row.airpfrom
        self.airpfromname = row.airpfromname
        self.cityto = row.cityto
        self.airpto = row.airpto
        self.airptoname = row.airptoname
        self.fltime = row.fltime
        self.price = row.price
        self.currency = row.currency
        self.customid = row.customid
        self.name = row.name


    def __str__(self):
        """Вывод."""
        return f'{self.bookid} {self.carrname} {self.cityfrom} {self.airpfrom} {self.airpfromname} \
                {self.cityto} {self.airpto } {self.airptoname} {self.fldate} {self.fltime} \
                {self.price} {self.currency} {self.carrcode} {self.connid} {self.name}'
    

    def __repr__(self):
        """Представление."""
        return self.__str__()
