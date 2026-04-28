"""DTO для рейсов."""
from datetime import datetime


class SflightDTO:
    """DTO для рейсов."""
    def __init__(self,row):
        """Конструктор."""
        self.mandt = row.mandt
        self.carrid = row.carrid
        self.connid = row.connid
        if isinstance(row.fldate, str):
            year, month, day  = map(int, row.fldate.split('-'))
            self.fldate = datetime(year, month, day).date()
        else:
            self.fldate = row.fldate

    def __str__(self):
        """Вывод."""
        return f'{self.mandt} {self.carrid} {self.connid} {self.fldate}'
    
    def __repr__(self):
        """Представление."""
        return self.__str__()
