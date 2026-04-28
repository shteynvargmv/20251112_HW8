"""DTO для рейсов и расписаний."""


class SpfliSflightDTO:
    """DTO для рейсов и расписаний."""
    def __init__(self,row):
        """Конструктор."""
        self.mandt = row.mandt
        self.carrid = row.carrid
        self.carrcode = row.carrcode
        self.connid = row.connid
        self.countryfr = row.countryfr
        self.cityfrom = row.cityfrom
        self.airpfrom = row.airpfrom
        self.airpfrom_name = row.airpfrom_name
        self.countryto = row.countryto
        self.cityto = row.cityto
        self.airpto = row.airpto
        self.airpto_name = row.airpto_name
        self.fltime = row.fltime
        self.fldate = row.fldate
        self.price = row.price
        self.currency = row.currency
        self.planetype = row.planetype
        self.seatsmax = row.seatsmax
        self.seatsocc = row.seatsocc
        self.seatsfree = int(row.seatsmax) - int(row.seatsocc)

    def __str__(self):
        """Вывод."""
        return f'{self.mandt} {self.carrid} {self.carrcode} {self.connid} {self.countryfr} {self.cityfrom} {self.airpfrom} \
                {self.airpfrom_name} {self.countryto} {self.cityto} {self.airpto} {self.airpto_name} {self.fltime} \
                {self.fldate} {self.price} {self.currency} {self.planetype} {self.seatsmax} {self.seatsocc}'
    
    def __repr__(self):
        """Представление."""
        return self.__str__()

