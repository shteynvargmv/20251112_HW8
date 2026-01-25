"""Репозиторий."""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from dotenv import dotenv_values
from sqlalchemy import func, select, text
from sqlalchemy.orm import sessionmaker

from db.engine import Engine
from db.models import SBook, SCustom, SPFli

# from services.generator import Generator

env_path = Path(__file__).parent.parent / '.env'
mandt=dotenv_values(env_path)['MANDT']

class FlyRepository:
    """Репозиторий."""
    def __init__(self, **kwargs):
        """Конструктор."""
        if not kwargs:
            engine = Engine()
            # engine.run()
            self.engine = engine.get_engine()    
            self.conn = engine.get_conn()
            session_f = sessionmaker(bind=self.conn)
            self.session = session_f()
        else:
            self.session = kwargs.get('session')
            self.conn = self.session.connection()
            self.engine = self.session.bind

    def form_where(self,fields,values):
        """Сформировать where."""
        if len(fields) == len(values):
            wheres = []
            for i in range(len(fields)):
                wheres.append(f"{fields[i]} = '{values[i]}'")    
            where = ' AND '.join(wheres)
            return where
    
    def select_all(self,db_name):
        """Получить все записи таблицы."""
        res = self.session.execute(text(f'SELECT * FROM {db_name}'))  # noqa: S608
        return res.fetchall()
        
    def select(self, db_name, fields, values):
        """Поличить записи таблицы db_name where fields=values."""
        where = self.form_where(fields, values)
        if where != '':
            res = self.session.execute(text(f'SELECT * FROM {db_name} WHERE {where}'))  # noqa: S608
            return res.fetchall()
        
    def select_scustom(self, fields, values):
        """Получить записи таблицы пользователей."""
        where = self.form_where(fields, values)
        if where != '':
            stmt = select(SCustom).from_statement(text(f'SELECT * FROM scustom WHERE {where}'))  # noqa: S608
            result = self.session.execute(stmt)  
            return result.scalars().all()
        
    def insert_scustom(self, scustom):   
        """Добавить нового пользователя."""  
        self.session.add(scustom)
        self.session.commit()              
    
    def generate(self,count):
        """Генератор, сейчас не используется, реализовано через alembic."""
        # generator = Generator(self.engine)
        # generator.add(count)

    def select_spfli(self):
        """Получить записи из spfli."""
        stmt = select(SPFli).from_statement(text('SELECT * FROM spfli'))
        result = self.session.execute(stmt)  
        return result.scalars().all()
        
    def select_sflight(self, fields, values):
        """Получить записи из sflight."""
        where = self.form_where(fields, values)
        if where != '':
            stmt = text(f"""
                SELECT 
                    mandt,
                    carrid,
                    connid,
                    fldate
                    FROM sflight WHERE {where}""")  # noqa: S608
            result = self.session.execute(stmt)
            return result
        
    def select_spfli_sflight(self, fields, values):
        """Получить записи из spfli + sflight."""
        where = self.form_where(fields, values)
        if where != '':
            stmt = text(f"""
                SELECT
                    sflight.carrid,
                    scarr.carrcode,
                    sflight.connid, 
                    spfli.countryfr,
                    spfli.cityfrom,
                    spfli.airpfrom,
                    af.name as airpfrom_name,
                    spfli.countryto,
                    spfli.cityto,
                    spfli.airpto,
                    at.name as airpto_name,
                    spfli.fltime, 
                    sflight.fldate,
                    sflight.price,
                    sflight.currency,
                    sflight.planetype,
                    sflight.seatsmax,
                    sflight.seatsocc, 
                    sflight.mandt                       
                    FROM spfli
                    INNER JOIN sflight 
                        ON spfli.mandt = sflight.mandt AND spfli.carrid = sflight.carrid AND spfli.connid = sflight.connid  
                    INNER JOIN sairport as af
                        ON spfli.mandt = af.mandt AND spfli.airpfrom = af.id    
                    INNER JOIN sairport as at
                        ON spfli.mandt = at.mandt AND spfli.airpto = at.id   
                    INNER JOIN scarr 
                        ON spfli.mandt = scarr.mandt AND spfli.carrid = scarr.carrid                    
                    WHERE {where}""")  # noqa: S608
            result = self.session.execute(stmt)
            return result
            
    def select_sbook(self, fields, values):
        """Получить данные из sbook."""
        where = self.form_where(fields, values)
        if where != '':
            stmt = text(f"""
                SELECT
                    sbook.mandt,
                    sbook.carrid,
                    scarr.carrcode,
                    sbook.connid,
                    sbook.fldate,
                    sbook.bookid,
                    sbook.customid,
                    scustom.name                       
                    FROM sbook
                    INNER JOIN scarr 
                        ON sbook.mandt = scarr.mandt AND sbook.carrid = scarr.carrid 
                    INNER JOIN scustom
                        ON sbook.mandt = scustom.mandt AND sbook.customid = scustom.phone                       
                    WHERE {where}""")  # noqa: S608
            result = self.session.execute(stmt)
            return result    
            
    def get_max_bookid_sbook(self):   
        """Максимальный bookid в sbook."""   
        stmt = select(func.max(SBook.bookid))      
        max_bookid = self.session.execute(stmt).scalar()
        if not max_bookid:
            max_bookid = 0
        return max_bookid
            
    def update_sflight(self, sflight):
        """Обновить sfplight."""
        self.session.merge(sflight)
        self.session.commit()  

    def update_sbook(self, sbook):
        """Обновить sbook."""
        self.session.merge(sbook)
        self.session.commit()   

    def close(self):
        """Закрыть все."""
        self.session.close()
        self.conn.close()
        self.engine.dispose()

