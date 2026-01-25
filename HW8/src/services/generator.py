"""Генератор, сейчас не используется, реализовано через alembic."""
# import sys
# from pathlib import Path
# sys.path.append(str(Path(__file__).parent.parent / 'db'))
# from db.models import SAirport,SCarr,SPFli,SFlight
# from faker import Faker
# import random
# from sqlalchemy.orm import Session

# import sys
# from pathlib import Path
# sys.path.append(sys.path.append(str(Path(__file__).parent)))

# from dotenv import dotenv_values

# env_path = Path(__file__).parent.parent / '.env'
# mandt=dotenv_values(env_path)['MANDT']

# class Generator:
#     def __init__(self, engine):
#         self.engine = engine

#     def add(self,count):
#         utc_timezones = [
#             "UTC-12", "UTC-11", "UTC-10", "UTC-9:30", "UTC-9", "UTC-8", 
#             "UTC-7", "UTC-6", "UTC-5", "UTC-4", "UTC-3:30", "UTC-3", 
#             "UTC-2", "UTC-1", "UTC±0", "UTC+1", "UTC+2", "UTC+3", 
#             "UTC+3:30", "UTC+4", "UTC+4:30", "UTC+5", "UTC+5:30", 
#             "UTC+5:45", "UTC+6", "UTC+6:30", "UTC+7", "UTC+8", 
#             "UTC+8:45", "UTC+9", "UTC+9:30", "UTC+10", "UTC+10:30", 
#             "UTC+11", "UTC+12", "UTC+12:45", "UTC+13", "UTC+14"
#         ]
        
#         faker = Faker()        

#         connids = []
#         while len(connids) < count*3:
#             connid = faker.numerify(text='####')
#             if connid not in connids:
#                 connids.append(connid)

#         names = []
#         while len(names) < count:
#             name = faker.city()[:3].upper()
#             if name not in names:
#                 names.append(name)

#         data_first = []
#         data_second = []
#         for i in range(count):
#             data_first.append(SAirport(
#                 mandt=mandt,
#                 id=i+1,
#                 name=names[i],
#                 timezone=random.choice(utc_timezones)))

#         for i in range(count*3):
#             carrname = faker.word().capitalize()
#             data_first.append(SCarr(
#                 mandt=mandt,
#                 carrid=i, 
#                 carrname=carrname, 
#                 carrcode=carrname[:2].upper(), 
#                 url=faker.url()))
            
#         for i in range(count):
#             cityfrom=faker.city()
#             cityto=faker.city()
#             fldate=faker.future_date(end_date='+365d')
        
#             for j in range(random.randint(1,3)):                     
#                 airpfrom=random.randint(1,count)
#                 airpto=random.randint(1,count)
#                 while airpto == airpfrom:
#                         airpto=random.randint(1,count)  
    
#                 data_first.append(SPFli(
#                     mandt = mandt,
#                     carrid=i*3+j,
#                     connid=connids[i*3+j],
#                     countryfr=faker.country(),
#                     cityfrom=cityfrom,
#                     airpfrom=airpfrom,
#                     countryto=faker.country(),
#                     cityto=cityto,
#                     airpto=airpto,
#                     fltime=faker.time()
#                     ))
    
#                 airpfrom=''
#                 airpto=''
            
#                 data_second.append(SFlight(
#                     carrid=i*3+j,
#                     connid=connids[i*3+j],
#                     fldate=fldate,
#                     price=faker.pydecimal(left_digits=5,right_digits=2,positive=True,min_value=100,max_value=10000),
#                     currency=faker.currency()[0],
#                     planetype=faker.bothify(text='?').upper()+faker.numerify(text='###'),
#                     seatsmax=random.randint(180,200),
#                     seatsocc=random.randint(1,180)
#                 ))

#         with Session(self.engine) as session:
#             with session.begin():
#                 session.add_all(data_first)
#             with session.begin():
#                 session.add_all(data_second)

