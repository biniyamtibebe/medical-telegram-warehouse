import os
import cv2
import pandas as pd
import psycopg2
import torch
from ultralytics import YOLO
from dotenv import load_dotenv

# ------------------------------------------------------------------
# Environment & Model Setup
# ------------------------------------------------------------------

load_dotenv(
    r"C:\Users\hp\Desktop\medical-telegram-warehouse\medical-telegram-warehouse\.env"
)

# Allowlist YOLO for torch serialization safety
torch.serialization.add_safe_globals([YOLO])

# Database connection parameters
conn_params = {
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
}

# Load YOLOv8 Nano model (fast & lightweight)
model = YOLO("yolov8n.pt")

# ------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------

def categorize_detections(detections):
    """
    Categorize image based on detected objects.
    """
    has_person = any(cls == "person" for cls, _ in detections)
    has_product = any(cls in ["bottle", "cup"] for cls, _ in detections)

    if has_person and has_product:
        return "promotional"
    elif has_product:
        return "product_display"
    elif has_person:
        return "lifestyle"
    else:
        return "other"


# ------------------------------------------------------------------
# YOLO Detection Pipeline
# ------------------------------------------------------------------

def run_detection(image_root_dir):
    """
    Runs YOLO detection on all images and saves results to CSV.
    """
    results = []

    for channel_name in os.listdir(image_root_dir):
        channel_path = os.path.join(image_root_dir, channel_name)

        if not os.path.isdir(channel_path):
            continue

        for img_file in os.listdir(channel_path):
            if not img_file.lower().endswith(".jpg"):
                continue

            img_path = os.path.join(channel_path, img_file)

            # ✅ Validate image before inference
            img = cv2.imread(img_path)
            if img is None:
                print(f"Skipping unreadable image: {img_path}")
                continue

            try:
                message_id = int(os.path.splitext(img_file)[0])

                yolo_results = model(img_path, verbose=False)

                if not yolo_results or yolo_results[0].boxes is None:
                    continue

                detections = [
                    (model.names[int(cls)], float(conf))
                    for cls, conf in zip(
                        yolo_results[0].boxes.cls,
                        yolo_results[0].boxes.conf,
                    )
                ]

                if not detections:
                    continue

                category = categorize_detections(detections)

                for cls, conf in detections:
                    results.append(
                        {
                            "message_id": message_id,
                            "channel_name": channel_name,
                            "detected_class": cls,
                            "confidence_score": conf,
                            "image_category": category,
                        }
                    )

            except Exception as e:
                print(f"Error processing {img_path}: {e}")
                continue

    output_csv = (
        r"C:\Users\hp\Desktop\medical-telegram-warehouse"
        r"\medical-telegram-warehouse\data\yolo_results.csv"
    )

    pd.DataFrame(results).to_csv(output_csv, index=False)
    return output_csv


# ------------------------------------------------------------------
# Database Load
# ------------------------------------------------------------------

def load_yolo_results_to_db(conn, csv_path):
    """
    Loads YOLO detection results into PostgreSQL.
    """
    df = pd.read_csv(csv_path)

    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS raw.image_detections (
                message_id BIGINT,
                channel_name TEXT,
                detected_class TEXT,
                confidence_score FLOAT,
                image_category TEXT
            );
            """
        )

        for _, row in df.iterrows():
            cur.execute(
                """
                INSERT INTO raw.image_detections
                (message_id, channel_name, detected_class, confidence_score, image_category)
                VALUES (%s, %s, %s, %s, %s);
                """,
                tuple(row),
            )

    conn.commit()


# ------------------------------------------------------------------
# Main Execution
# ------------------------------------------------------------------

if __name__ == "__main__":
    image_dir = r"data\raw\images"

    csv_path = run_detection(image_dir)

    conn = psycopg2.connect(**conn_params)
    load_yolo_results_to_db(conn, csv_path)
    conn.close()

    print("YOLO detection pipeline completed successfully.")
