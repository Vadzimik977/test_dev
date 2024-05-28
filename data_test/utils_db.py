from data_test import config
import psycopg2
import psycopg2.extras
from psycopg2.extras import RealDictCursor
from contextlib import closing
import time
import datetime

params_db = {'dbname': config.DB_NAME, 'user': config.DB_USER, 'password': config.DB_PASSWORD,
             'host': config.DB_HOST, 'port': config.DB_PORT, 'cursor_factory': psycopg2.extras.RealDictCursor}

# profile info
def get_profile_info(user_id):
    with closing(psycopg2.connect(**config.params_db)) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT name, user_name FROM test_users WHERE user_id = %s', (str(user_id),))
            result = cursor.fetchone()
            return result



# User id in db check
def user_id_in_db(user_id):
    with closing(psycopg2.connect(**params_db)) as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT exists (SELECT 1 FROM test_users WHERE user_id = %d LIMIT 1)' % user_id)
            return cursor.fetchone()['exists']

# User add
def add_user(user_id):
    with closing(psycopg2.connect(**params_db)) as conn:
        with conn.cursor() as cursor:
            cursor.execute('INSERT INTO test_users (user_id, stage) VALUES (%s, %s)', (user_id, 'get_name'))
            conn.commit()
# Name add
def add_name(user_id, name):
    with closing(psycopg2.connect(**params_db)) as conn:
        with conn.cursor() as cursor:
            cursor.execute('UPDATE test_users SET name = %s WHERE user_id = %s', (name, user_id))
            conn.commit()
# User_name input and check
def add_username(user_id, username):
    with closing(psycopg2.connect(**params_db)) as conn:
        with conn.cursor() as cursor:
            cursor.execute('UPDATE test_users SET user_name = %s WHERE user_id = %s', (username, user_id))
            conn.commit()

def username_exists(username):
    with closing(psycopg2.connect(**params_db)) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT EXISTS (SELECT 1 FROM test_users WHERE user_name = %s LIMIT 1)', (username,))
            return cursor.fetchone()['exists']

# Stages of registration
def get_stage(user_id):
    with closing(psycopg2.connect(**params_db)) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT stage FROM test_users WHERE user_id = %s', (user_id,))
            result = cursor.fetchone()
            return result['stage'] if result else None

def update_stage(user_id, stage):
    with closing(psycopg2.connect(**params_db)) as conn:
        with conn.cursor() as cursor:
            cursor.execute('UPDATE test_users SET stage = %s WHERE user_id = %s', (stage, user_id))
            conn.commit()

# tasks

def generate_id():
    return int('{:0<17}'.format(str(time.time()).replace('.', '')))

def update_temp_task(user_id, task_title=None, unique_id=None):
    with closing(psycopg2.connect(**params_db)) as conn:
        with conn.cursor() as cursor:
            if task_title is not None:
                cursor.execute('''
                    UPDATE tasks
                    SET task_title = %s, is_temp = TRUE
                    WHERE user_id = %s AND is_temp = TRUE
                ''', (task_title, user_id))
            if unique_id is not None:
                cursor.execute('''
                    INSERT INTO tasks (user_id, unique_id, is_temp)
                    VALUES (%s, %s, TRUE)
                ''', (user_id, unique_id))
            conn.commit()

def get_temp_task(user_id):
    with closing(psycopg2.connect(**params_db)) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT * FROM tasks WHERE user_id = %s AND is_temp = TRUE', (user_id,))
            return cursor.fetchone()

def clear_temp_task(user_id):
    with closing(psycopg2.connect(**params_db)) as conn:
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM tasks WHERE user_id = %s AND is_temp = TRUE', (user_id,))
            conn.commit()

def add_task(user_id, task_title, task_description, unique_id):
    with closing(psycopg2.connect(**params_db)) as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                UPDATE tasks
                SET task_title = %s, task_description = %s, is_temp = FALSE
                WHERE user_id = %s AND unique_id = %s AND is_temp = TRUE
            ''', (task_title, task_description, user_id, unique_id))
            conn.commit()

# get tasks list

def get_tasks(user_id,offset, TASKS_PER_PAGE):
    with closing(psycopg2.connect(**params_db)) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT task_title, unique_id,done FROM tasks WHERE user_id = %s AND is_temp = FALSE LIMIT %s OFFSET %s', (str(user_id), TASKS_PER_PAGE, offset))
            tasks = cursor.fetchall()
            cursor.execute('SELECT COUNT(*) FROM tasks WHERE user_id = %s AND is_temp = FALSE', (str(user_id),))
            total_tasks = cursor.fetchone()['count']
            return tasks,total_tasks

# view task
def view_task(user_id,unique_id):
    with closing(psycopg2.connect(**config.params_db)) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT task_title, task_description FROM tasks WHERE user_id = %s AND unique_id = %s', (str(user_id), unique_id))
            task = cursor.fetchone()
            return task

# task done

def task_done(unique_id):
    new_type=True
    with closing(psycopg2.connect(**params_db)) as conn:
        with conn.cursor() as cursor:
            cursor.execute('UPDATE tasks SET done = %s WHERE unique_id = %s', (new_type, unique_id))
            conn.commit()
# delete task
def delete_task(user_id,unique_id):
    with closing(psycopg2.connect(**config.params_db)) as conn:
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM tasks WHERE user_id = %s AND unique_id = %s', (str(user_id), unique_id))
            conn.commit()
