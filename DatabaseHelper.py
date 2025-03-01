import psycopg2
import os

DB_CONFIG = {
    "dbname": "image_processing",
    "user": "kanishk",
    "host": "localhost",
    "port": "5432",
}


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


def save_request(request_id, status):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO requests (id, status) VALUES (%s, %s)", (request_id, status))
    conn.commit()
    cur.close()
    conn.close()


def update_request_status(request_id, status):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE requests SET status = %s WHERE id = %s", (status, request_id))
    conn.commit()
    cur.close()
    conn.close()


def get_request_status(request_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT status FROM requests WHERE id = %s", (request_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row else "not found"


def delete_request_status(request_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("delete FROM requests WHERE id = %s", (request_id,))
    conn.commit()
    cur.close()
    conn.close()


def insert_image_link(request_id, serial_number, product_name, input_image_urls, output_image_urls):
    conn = get_db_connection()
    cur = conn.cursor()
    sql = """
    INSERT INTO public.image_links 
    (request_id, serial_number, product_name, input_image_urls, output_image_urls)
    VALUES (%s, %s, %s, %s, %s)
    """
    cur.execute(sql, (request_id, serial_number, product_name, input_image_urls, output_image_urls))
    conn.commit()
    cur.close()
    conn.close()
