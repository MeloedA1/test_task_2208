import psycopg2
from psycopg2.extras import execute_values

from config import cfg


PG_CONNECTION_PARAMS = {
    "user": cfg.pg_user,
    "password": cfg.pg_password,
    "database": cfg.pg_db,
    "host": cfg.pg_host,
    "port": 5432,
}


class PGWriter:
    def __init__(self):
        self._connection = psycopg2.connect(**PG_CONNECTION_PARAMS)

    def upload_data_to_db(self, data_rows):
        
        sql = """
        INSERT into public.products (id, order_num, dollar_value, ruble_value, delivery_time) VALUES %s
            ON CONFLICT (id) DO UPDATE
            SET id = EXCLUDED.id, order_num = EXCLUDED.order_num,
                dollar_value = EXCLUDED.dollar_value, ruble_value = EXCLUDED.ruble_value,
                delivery_time = EXCLUDED.delivery_time;
        """
        with self._connection as conn, conn.cursor() as cur:
            execute_values(
                cur, sql, self._transform_input_data(data_rows)
            )
       
    
    def get_expired_orders(self):
        
        sql = """select order_num, delivery_time from products where delivery_time < now();"""
        with self._connection as conn, conn.cursor(name="ss_cursor") as cur:
            cur.execute(sql)
            expired_orders = cur.fetchall()  
            return expired_orders

    def create_table(self):
        sql = """CREATE TABLE IF NOT EXISTS public.products (
                   id     integer,
                   order_num    text,
                   dollar_value integer,
                   ruble_value float8,
                   delivery_time date,
                   PRIMARY KEY(id)
                 );"""
        with self._connection as conn, conn.cursor() as cur:
            cur.execute(sql)
 
    @staticmethod
    def _transform_input_data(data_rows):
        return [(row['id'], row['order_num'], row['dollar_value'],
                 row['ruble_value'], row['delivery_time']) for row in data_rows]


