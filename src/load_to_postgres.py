import os
import json
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

load_dotenv(r"C:\Users\hp\Desktop\medical-telegram-warehouse\medical-telegram-warehouse\.env")

# DB connection from .env
conn_params = {
    'dbname': 'medical_telegram_warehouse',  # Update here
    'user': 'postgres',
    'password': 'Bine1234',  # Replace with your actual password
    'host': 'localhost',
    'port': '5432'
}

def create_raw_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE SCHEMA IF NOT EXISTS raw;
            CREATE TABLE IF NOT EXISTS raw.telegram_messages (
                message_id BIGINT,
                channel_name TEXT,
                message_date TIMESTAMP,
                message_text TEXT,
                has_media BOOLEAN,
                views INTEGER,
                forwards INTEGER,
                image_path TEXT
            );
        """)
    conn.commit()

def load_json_to_db(conn, json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    with conn.cursor() as cur:
        for msg in data:
            cur.execute("""
                INSERT INTO raw.telegram_messages 
                (message_id, channel_name, message_date, message_text, has_media, views, forwards, image_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (msg['message_id'], msg['channel_name'], msg['message_date'], msg['message_text'],
                  msg['has_media'], msg['views'], msg['forwards'], msg['image_path']))
    conn.commit()

if __name__ == '__main__':
    conn = psycopg2.connect(**conn_params)
    create_raw_table(conn)
    
    # Load all JSON files (recursive walk)
    for root, _, files in os.walk(r'data/raw/telegram_messages'):
        for file in files:
            if file.endswith('.json'):
                json_path = os.path.join(root, file)
                load_json_to_db(conn, json_path)
                print(f"Loaded {json_path}")
    
    conn.close()
