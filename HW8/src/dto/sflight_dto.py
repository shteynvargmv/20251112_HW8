
from datetime import datetime

class SflightDTO:
    def __init__(self,row):
        self.mandt = row.mandt
        self.carrid = row.carrid
        self.connid = row.connid
        if isinstance(row.fldate, str):
            year, month, day  = map(int, row.fldate.split('-'))
            self.fldate = datetime(year, month, day).date()
        else:
            self.fldate = row.fldate

    def __str__(self):
        return f"{self.mandt} {self.carrid} {self.connid} {self.fldate}"
    
    def __repr__(self):
        return self.__str__()
