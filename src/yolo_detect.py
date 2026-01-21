import os
import csv
import pandas as pd
from ultralytics import YOLO
from dotenv import load_dotenv
import psycopg2

load_dotenv()

# DB connection
conn_params = {  # Same as above
    'dbname': os.getenv('POSTGRES_DB'),
    # ... (fill similarly)
}

# Load YOLO model
model = YOLO('yolov8n.pt')  # Nano model for efficiency

def categorize_detections(detections):
    has_person = any(cls == 'person' for cls, _ in detections)
    has_product = any(cls in ['bottle', 'cup'] for cls, _ in detections)  # Example classes for products
    if has_person and has_product:
        return 'promotional'
    elif has_product:
        return 'product_display'
    elif has_person:
        return 'lifestyle'
    else:
        return 'other'

def run_detection(image_dir):
    results = []
    for channel_dir in os.listdir(image_dir):
        channel_path = os.path.join(image_dir, channel_dir)
        if os.path.isdir(channel_path):
            for img_file in os.listdir(channel_path):
                if img_file.endswith('.jpg'):
                    img_path = os.path.join(channel_path, img_file)
                    message_id = int(os.path.splitext(img_file)[0])
                    
                    # Run YOLO
                    yolo_results = model(img_path)
                    detections = [(model.names[int(cls)], conf) for cls, conf in zip(yolo_results[0].boxes.cls, yolo_results[0].boxes.conf)]
                    
                    category = categorize_detections(detections)
                    
                    for cls, conf in detections:
                        results.append({
                            'message_id': message_id,
                            'channel_name': channel_dir,
                            'detected_class': cls,
                            'confidence_score': conf,
                            'image_category': category
                        })
    
    # Save to CSV
    csv_path = 'data/yolo_results.csv'
    pd.DataFrame(results).to_csv(csv_path, index=False)
    return csv_path

def load_yolo_to_db(conn, csv_path):
    df = pd.read_csv(csv_path)
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS raw.image_detections (
                message_id BIGINT,
                channel_name TEXT,
                detected_class TEXT,
                confidence_score FLOAT,
                image_category TEXT
            );
        """)
        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO raw.image_detections VALUES (%s, %s, %s, %s, %s);
            """, tuple(row))
    conn.commit()

if __name__ == '__main__':
    image_dir = 'data/raw/images'
    csv_path = run_detection(image_dir)
    conn = psycopg2.connect(**conn_params)
    load_yolo_to_db(conn, csv_path)
    conn.close()