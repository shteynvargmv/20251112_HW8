"""DTO для бронирований."""
from datetime import datetime


class SBookDTO:
    """DTO для бронирований."""
    def __init__(self,row):
        """Конструктор."""
        self.mandt = row.mandt
        self.carrid = row.carrid
        self.carrcode = row.carrcode
        self.connid = row.connid
        if isinstance(row.fldate, str):
            year, month, day  = map(int, row.fldate.split('-'))
            self.fldate = datetime(year, month, day).date()
        else:
            self.fldate = row.fldate
        self.bookid = row.bookid
        self.customid = row.customid
        self.name = row.name

    def __str__(self):
        """Вывод."""
        return f'{self.mandt} {self.carrid} {self.carrcode} {self.connid} \
                {self.fldate} {self.bookid} {self.customid} {self.name}'
    
    def __repr__(self):
        """Представление."""
        return self.__str__()
