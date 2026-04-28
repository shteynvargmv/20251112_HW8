"""Схема для API post bookings."""
import sys
from datetime import date
from pathlib import Path as lPath

from pydantic import BaseModel, Field, model_validator

sys.path.append(str(lPath(__file__).parent.parent))

from services.fly_service import FlyService


class BookingSchema(BaseModel):
    """Схема для создания бронирования."""
    carrcode: str = Field(len=2)
    connid: str = Field(len=4)
    fldate: date = Field(future=True)
    pass_count: int = Field(gt=0, description='Количество пассажиров (билетов)')
    
    @model_validator(mode='after')
    def validate_booking(self) -> 'BookingSchema':
        """Валидация всех полей."""    
        if self.fldate <= date.today():
            raise ValueError(f'Дата вылета должна быть в будущем. Сегодня: {date.today()}')
        
        service = FlyService()
        sflights = service.get_spfli_sflight(('scarr.carrcode','spfli.connid', 'sflight.fldate' ),(self.carrcode,self.connid,self.fldate))

        if len(sflights) > 0:
            seatsfree = sflights[0].seatsfree
            if seatsfree < self.pass_count:
                raise ValueError(f'Свободных мест на рейсе {self.carrcode}{self.connid} {self.fldate}: {seatsfree}. Бронирование невозможно')
        else:
            raise ValueError(f'Рейс {self.carrcode}{self.connid} {self.fldate} не найден')
        
        return self

