from data_test import config
import psycopg2
import psycopg2.extras
from psycopg2.extras import RealDictCursor
from contextlib import closing


def init_db():
    with closing(psycopg2.connect(**config.params_db)) as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_users (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT UNIQUE,
                    name TEXT,
                    username TEXT UNIQUE,
                    stage TEXT
                )
            ''')
            conn.commit()
init_db()
