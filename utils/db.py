import psycopg2
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

def connect_to_supabase():
    try:
        conn = psycopg2.connect(
            host=os.getenv("SUPABASE_DB_HOST"),
            port=os.getenv("SUPABASE_DB_PORT"),
            dbname=os.getenv("SUPABASE_DB_NAME"),
            user=os.getenv("SUPABASE_DB_USER"),
            password=os.getenv("SUPABASE_DB_PASSWORD"),
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error al conectar: {e}")
        return None

def execute_query(query, conn=None, is_select=True):
    try:
        close_conn = False
        if conn is None:
            conn = connect_to_supabase()
            close_conn = True

        cursor = conn.cursor()
        cursor.execute(query)

        if is_select:
            results = cursor.fetchall()
            colnames = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(results, columns=colnames)
            result = df
        else:
            conn.commit()
            result = True

        cursor.close()
        if close_conn:
            conn.close()
        return result

    except Exception as e:
        print(f"Error ejecutando consulta: {e}")
        if conn and not is_select:
            conn.rollback()
        return pd.DataFrame() if is_select else False
