"""ORM модели."""
from datetime import date, time
from decimal import Decimal
from pathlib import Path
from typing import Optional

from dotenv import dotenv_values
from sqlalchemy import Date, ForeignKeyConstraint, Integer, Numeric, String, Time
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

env_path = Path(__file__).parent.parent / '.env'
mandt=dotenv_values(env_path)['MANDT']

class Base(DeclarativeBase):
    """Класс Base."""
    ...

class SCustom(Base):
    """Пользователи."""
    __tablename__='scustom'
    mandt: Mapped[str] = mapped_column(String(3), primary_key=True)
    phone: Mapped[str] = mapped_column(String(20),primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    #1:M
    sbook_customids: Mapped['SBook'] = relationship( 
        'SBook', 
        back_populates='scustom_phone',
        foreign_keys='[SBook.mandt, SBook.customid]',
        viewonly=True
    )

    def __init__(self, phone, name):
        """Конструктор."""
        self.mandt = mandt
        self.phone = phone
        self.name = name

    def __str__(self):
        """Вывод."""
        return f'{self.mandt} {self.name} ({self.phone})'

class SAirport(Base):
    """Аэропорты."""
    __tablename__ = 'sairport'
    mandt: Mapped[str] = mapped_column(String(3), primary_key=True)
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    timezone: Mapped[str] = mapped_column(String(50))
    #1:M
    spfli_airpfroms: Mapped[list['SPFli']] = relationship(
        'SPFli',
        back_populates='sairport_id_from',
        foreign_keys='[SPFli.mandt, SPFli.airpfrom]',
        viewonly=True
        )
    #1:M
    spfli_airptos: Mapped[list['SPFli']] = relationship(
        'SPFli',
        back_populates='sairport_id_to',
        foreign_keys='[SPFli.mandt, SPFli.airpto]',
        viewonly=True
        )
    
    def __init__(self, id, name, timezone):  # noqa: A002
        """Конструктор."""
        self.mandt = mandt
        self.id = id
        self.name = name
        self.timezone = timezone

class SPFli(Base):
    """Расписание рейсов."""
    __tablename__ = 'spfli'
    mandt: Mapped[str] = mapped_column(String(3), primary_key=True)
    carrid: Mapped[int] = mapped_column(Integer,primary_key=True)
    connid: Mapped[str] = mapped_column(String(4),primary_key=True)
    countryfr: Mapped[str] = mapped_column(String(100))
    cityfrom: Mapped[str] = mapped_column(String(100)) 
    airpfrom: Mapped[int] = mapped_column(Integer)
    countryto: Mapped[str] = mapped_column(String(100))
    cityto: Mapped[str] = mapped_column(String(100))
    airpto: Mapped[int] = mapped_column(Integer)
    fltime:  Mapped[Optional[time]] = mapped_column(Time)

    __table_args__ = (
        ForeignKeyConstraint(
            ['mandt', 'carrid'], 
            ['scarr.mandt', 'scarr.carrid']
        ),
        ForeignKeyConstraint(
            ['mandt', 'airpfrom'], 
            ['sairport.mandt', 'sairport.id']
        ),
        ForeignKeyConstraint(
            ['mandt', 'airpto'], 
            ['sairport.mandt', 'sairport.id']
        )
    )

    #M:1
    scarr_carrid_spfli: Mapped['SCarr'] = relationship( 
        'SCarr', 
        back_populates='spfli_carrids',
        foreign_keys=[mandt, carrid],
        viewonly=True
    )
    #M:1
    sairport_id_from: Mapped['SAirport'] = relationship(
        'SAirport',
        back_populates='spfli_airpfroms',
        foreign_keys=[mandt, airpfrom],
        viewonly=True
    )
    #M:1
    sairport_id_to: Mapped['SAirport'] = relationship(
        'SAirport',
        back_populates='spfli_airptos',
        foreign_keys=[mandt, airpto],
        viewonly=True
    )
    #1:M
    sflight_carrids_connids: Mapped[list['SFlight']] = relationship(
        'SFlight',
        back_populates='spfli_carrid_connid',
        foreign_keys='[SFlight.mandt, SFlight.carrid, SFlight.connid]',
        viewonly=True
        )
    
    def __init__(self, carrid, connid, countryfr, cityfrom, 
                airpfrom, countryto, cityto, airpto, fltime):
        """Конструктор."""
        self.mandt = mandt
        self.carrid = carrid
        self.connid = connid
        self.countryfr = countryfr
        self.cityfrom = cityfrom
        self.airpfrom = airpfrom
        self.countryto = countryto
        self.cityto = cityto
        self.airpto = airpto
        self.fltime = fltime

class SFlight(Base):
    """Рейсы."""
    __tablename__ = 'sflight'
    mandt: Mapped[str] = mapped_column(String(3), primary_key=True)
    carrid: Mapped[int] = mapped_column(Integer,primary_key=True)
    connid: Mapped[str] = mapped_column(String(4),primary_key=True)
    fldate: Mapped[Optional[date]] = mapped_column(Date,primary_key=True)
    price: Mapped[Optional[Decimal]] = mapped_column(Numeric(16, 2))
    currency: Mapped[Optional[str]] = mapped_column(String(5))
    planetype: Mapped[Optional[str]] = mapped_column(String(10))
    seatsmax: Mapped[Optional[int]] = mapped_column(Integer)
    seatsocc: Mapped[Optional[int]] = mapped_column(Integer)

    __table_args__ = (
        ForeignKeyConstraint(
            ['mandt', 'carrid', 'connid'], 
            ['spfli.mandt', 'spfli.carrid', 'spfli.connid']
        ),
    )

    #M:1
    spfli_carrid_connid: Mapped['SPFli'] = relationship( 
        'SPFli', 
        back_populates='sflight_carrids_connids',
        foreign_keys=[mandt, carrid, connid],
        viewonly=True
    ) 

    #1:M
    sbook_carrids_connids_fldates: Mapped[list['SBook']] = relationship(
        'SBook',
        back_populates='sflight_carrid_connid_fldate',
        foreign_keys='[SBook.mandt, SBook.carrid, SBook.connid, SBook.fldate]',
        viewonly=True
        ) 

    def __init__(self, carrid, connid, fldate, price, 
                currency, planetype, seatsmax, seatsocc):
        """Конструктор."""
        self.mandt = mandt
        self.carrid = carrid
        self.connid = connid
        self.fldate = fldate
        self.price = price
        self.currency = currency
        self.planetype = planetype
        self.seatsmax = seatsmax
        self.seatsocc = seatsocc

class SCarr(Base):
    """Авиакомпания."""
    __tablename__ = 'scarr'    
    mandt: Mapped[str] = mapped_column(String(3), primary_key=True) 
    carrid: Mapped[int] = mapped_column(Integer, primary_key=True)
    carrname: Mapped[Optional[str]] = mapped_column(String(20))
    carrcode: Mapped[Optional[str]] = mapped_column(String(5))
    url: Mapped[Optional[str]] = mapped_column(String(255))

    #1:M
    spfli_carrids: Mapped[list['SPFli']] = relationship(
        'SPFli',
        back_populates='scarr_carrid_spfli',
        foreign_keys='[SPFli.carrid, SPFli.mandt]',
        viewonly=True
        )
    
    #1:M
    sbook_carrids: Mapped[list['SBook']] = relationship(
        'SBook',
        back_populates='scarr_carrid_sbook',
        foreign_keys='[SBook.carrid, SBook.mandt]',
        viewonly=True
        )
    
    def __init__(self, carrid, carrname, carrcode, url):
        """Конструктор."""
        self.mandt = mandt
        self.carrid = carrid
        self.carrname = carrname
        self.carrcode = carrcode
        self.url = url

class SBook(Base):
    """Бронирования."""
    __tablename__ = 'sbook'  
    mandt: Mapped[str] = mapped_column(String(3), primary_key=True)  
    carrid: Mapped[int] = mapped_column(Integer, primary_key=True)
    connid: Mapped[str] = mapped_column(String(4), primary_key=True)
    fldate: Mapped[date] = mapped_column(Date, primary_key=True)
    bookid: Mapped[int] = mapped_column(Integer, primary_key=True)
    customid: Mapped[Optional[str]] = mapped_column(String(20))

    __table_args__ = (
        ForeignKeyConstraint(
            ['mandt', 'carrid', 'connid', 'fldate'], 
            ['sflight.mandt', 'sflight.carrid', 'sflight.connid', 'sflight.fldate']
        ),
        ForeignKeyConstraint(
            ['mandt', 'carrid'], 
            ['scarr.mandt', 'scarr.carrid']
        ),
        ForeignKeyConstraint(
            ['mandt', 'carrid'], 
            ['scarr.mandt', 'scarr.carrid']
        ),
        ForeignKeyConstraint(
            ['mandt', 'customid'], 
            ['scustom.mandt', 'scustom.phone']
        )

    )

    #M:1
    sflight_carrid_connid_fldate: Mapped['SFlight'] = relationship( 
        'SFlight', 
        back_populates='sbook_carrids_connids_fldates',
        foreign_keys=[mandt, carrid, connid, fldate],
        viewonly=True
    ) 

    #M:1
    scarr_carrid_sbook: Mapped['SCarr'] = relationship( 
        'SCarr', 
        back_populates='sbook_carrids',
        foreign_keys=[mandt, carrid],
        viewonly=True
    )

    #M:1
    scustom_phone: Mapped['SCustom'] = relationship( 
        'SCustom', 
        back_populates='sbook_customids',
        foreign_keys=[mandt, customid],
        viewonly=True
    )

    def __init__(self, carrid, connid, fldate, bookid, customid):
        """Конструктор."""
        self.mandt = mandt
        self.carrid = carrid
        self.connid = connid
        self.fldate = fldate
        self.bookid = bookid
        self.customid = customid    