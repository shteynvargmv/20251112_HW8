"""Сервис."""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from types import SimpleNamespace

from db.cache import cache_clear, cache_pull, cache_push
from repositories.fly_repository import FlyRepository

sys.path.append(str(Path(__file__).parent / 'dto'))
from db.models import SBook, SFlight
from dto.sbook_dto import SBookDTO
from dto.sflight_dto import SflightDTO
from dto.spfli_sflight_dto import SpfliSflightDTO

spfli_sflight_cache_key = 'spfli_sflight'
sflight_cache_key = 'sflight'

class FlyService:
    """Сервис."""

    def __init__(self, **kwargs):
        """Конструктор."""
        self.repository = FlyRepository(**kwargs)
        if not kwargs:
            self.customid = ''
        else:
            self.customid = kwargs.get('customid')
        cache_clear(spfli_sflight_cache_key, sflight_cache_key)

    def set_customid(self, customid):
        """Получить customid."""
        self.customid = customid

    def generate(self,count):
        """Сгенерировать count записей в БД, сейчас реализовано через alembic."""
        ...# return self.repository.generate(count)
    
    def get_all(self,db_name):
        """Получить все записи таблицы."""
        return self.repository.select_all(db_name)
        
    def get(self, db_name, fields, values):
        """Поличить записи таблицы db_name where fields=values."""
        return self.repository.select(db_name, fields, values)
    
    def get_scustom(self, fields, values):
        """Получить записи таблицы пользователей."""
        result = self.repository.select_scustom(fields, values)
        if result:
            self.customid = result[0].phone
        return result
    
    def add_scustom(self, scustom):
        """Добавить нового пользователя."""
        self.customid = scustom.phone
        return self.repository.insert_scustom(scustom)
    
    def get_spfli(self):
        """Получить записи из spfli."""
        return self.repository.select_spfli()
    
    def get_sflight(self, fields, values):
        """Получить записи из sflight."""
        #Сначала посмотрим, загружены ли такие в кэш
        cache_json = cache_pull(sflight_cache_key)
        cache=[]
        sflights=[]        
        for row in cache_json:
            data = SimpleNamespace(**row) 
            sflight = SflightDTO(data)
            cache.append(sflight)
            all_match = all( getattr(sflight, fields[i]) == values[i] for i in range(len(fields)))
            if all_match:
                sflights.append(sflight)
        if len(sflights) > 0:
            return sflights
        else:
            #Если нет, то возьмем из БД
            result = list(self.repository.select_sflight(fields,values))        
            for row in result:
                sflight = SflightDTO(row._mapping)
                sflights.append(sflight)       
            cache_push(sflight_cache_key,sflights+cache,3600) 
            return sflights 
    
    def get_spfli_sflight(self,fields,values):
        """Получить записи из spfli + sflight."""
        #Сначала посмотрим, загружены ли такие в кэш
        cache_json = cache_pull(spfli_sflight_cache_key)
        cache=[]
        dtos=[]        
        for row in cache_json:
            data = SimpleNamespace(**row) 
            dto = SpfliSflightDTO(data)
            cache.append(dto)
            all_match = all( getattr(dto, fields[i].split('.')[1]) == values[i] for i in range(len(fields)))          
            if all_match:
                dtos.append(dto)
        if len(dtos) > 0:
            return dtos
        else:
            #Если нет, то возьмем из БД
            result = list(self.repository.select_spfli_sflight(fields,values))        
            for row in result:
                dto = SpfliSflightDTO(row._mapping)
                dtos.append(dto)         
            cache_push(spfli_sflight_cache_key,dtos+cache,3600) 
            return dtos   
    
    def get_cache_spfli_sflight(self):
        """Получить записи из кэша spfli + sflight."""
        cache_json = cache_pull(spfli_sflight_cache_key) 
        fly_dtos=[]
        for row in cache_json:
            data = SimpleNamespace(**row) 
            flight_dto = SpfliSflightDTO(data)
            fly_dtos.append(flight_dto)
        return fly_dtos
    
    def set_cache_spfli_sflight(self,fly_dtos):
        """Отправить записи в кэш spfli + sflight."""
        cache_push(spfli_sflight_cache_key,fly_dtos,3600) 
    
    def update_sflight(self,fly_dto:SpfliSflightDTO):
        """Обновить sfplight."""
        sflight = SFlight(
            carrid = fly_dto.carrid,
            connid = fly_dto.connid, 
            fldate = fly_dto.fldate, 
            price = fly_dto.price, 
            currency = fly_dto.currency, 
            planetype = fly_dto.planetype, 
            seatsmax = fly_dto.seatsmax, 
            seatsocc = fly_dto.seatsocc)
        self.repository.update_sflight(sflight)

    def update_sbook(self,fly_dto:SBookDTO, pass_count):
        """Обновить sbook."""
        bookid = self.repository.get_max_bookid_sbook()
        for _ in range(pass_count):
            bookid += 1
            sbook = SBook(
                carrid = fly_dto.carrid,
                connid = fly_dto.connid, 
                fldate = fly_dto.fldate, 
                customid = self.customid,
                bookid = bookid)
            self.repository.update_sbook(sbook)

    def get_bookings(self):
        """Получить данные из sbook."""
        if self.customid:
            result = list(self.repository.select_sbook(('customid',),(self.customid,)))
            sbook_dtos = []
            for row in result:
                dto = SBookDTO(row._mapping)
                sbook_dtos.append(dto)  
            return sbook_dtos

    # def print_all(self):
    #     print('------------------------------------')
    #     rows = self.get_all('sairport')
    #     for row in rows:
    #         print(row)
    #     print('------------------------------------')
    #     rows = self.get_all('scarr')
    #     for row in rows:
    #         print(row)
    #     print('------------------------------------')
    #     rows = self.get_all('spfli')
    #     for row in rows:
    #         print(row)
    #     print('------------------------------------')
    #     rows = self.get_all('sflight')
    #     for row in rows:
    #         print(row)
    #     print('------------------------------------')
    #     rows = self.get_all('scustom')
    #     for row in rows:
    #         print(row)
    #     print('------------------------------------')

    def close(self):
        """Закрыть соединение."""
        self.repository.close()
        
