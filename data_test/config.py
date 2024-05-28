import psycopg2
import psycopg2.extras
API_ID=23699754
API_HASH='07ce00357bb6aab2fba4036b621b2d5c'
BOT_TOKEN = "7133086922:AAGNEmNMBYkdw9qn9rVrXNiZJ8qw-LEYB9I"

DB_NAME = 'db_astro'
DB_USER = 'zhuravlev'
DB_PASSWORD = 'Ouhdsouvnrp!'
DB_HOST = 'rc1a-b3k465v2eu1ro026.mdb.yandexcloud.net'
DB_PORT = 6432
params_db = {'dbname': DB_NAME, 'user': DB_USER, 'password': DB_PASSWORD,
             'host': DB_HOST, 'port': DB_PORT, 'cursor_factory': psycopg2.extras.RealDictCursor}
