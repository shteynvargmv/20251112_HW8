"""Engine."""
import sys
from pathlib import Path

from dotenv import dotenv_values
from sqlalchemy import URL, create_engine

sys.path.append(str(Path(__file__).parent))

class Engine:
    """Engine."""
    def __init__(self):
        """Конструктор."""
        env_path = Path(__file__).parent.parent / '.env'
        config = dotenv_values(env_path)
        user=config['POSTGRES_USER']
        password=config['POSTGRES_PASSWORD']
        host=config['POSTGRES_HOST']
        port=config['POSTGRES_PORT']
        database=config['POSTGRES_DATABASE']
        dialect='postgresql'
        driver='psycopg2'

        url_object=URL.create(
            f'{dialect}+{driver}',
            username=user,
            password=password,
            host=host,
            port=port,
            database=database
            )
        
        engine = create_engine(url_object)
        self.engine = engine
        self.conn = self.engine.connect()

    # def run(self):
        # ...
        # with self.engine.connect() as conn:
            
        #     conn.execute(text('DROP TABLE IF EXISTS songtable CASCADE'))
        #     # Дочерние таблицы (с foreign keys)
        #     conn.execute(text('DROP TABLE IF EXISTS sbook CASCADE'))
        #     conn.execute(text('DROP TABLE IF EXISTS sflight CASCADE'))
        #     conn.execute(text('DROP TABLE IF EXISTS spfli CASCADE'))
            
        #     # Родительские таблицы
        #     conn.execute(text('DROP TABLE IF EXISTS scustom CASCADE'))
        #     conn.execute(text('DROP TABLE IF EXISTS sairport CASCADE'))
        #     conn.execute(text('DROP TABLE IF EXISTS scarr CASCADE'))
        #     conn.commit()
        #     print('Deleted')

        # try:
        #     Base.metadata.create_all(self.engine)
        # except Exception as e:
        #     print('Err' + e)  

    def get_conn(self):
        """Получить соединение."""
        return self.conn

    def get_engine(self):
        """Получить engine."""
        return self.engine


