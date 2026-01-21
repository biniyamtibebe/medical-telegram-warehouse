from dagster import op, job, ScheduleDefinition, repository
import subprocess
import os

@op
def scrape_telegram_data():
    subprocess.run(["python", "src/scraper.py"], check=True)

@op
def load_raw_to_postgres():
    subprocess.run(["python", "src/load_to_postgres.py"], check=True)

@op
def run_dbt_transformations():
    os.chdir("medical_warehouse")
    subprocess.run(["dbt", "run"], check=True)
    subprocess.run(["dbt", "test"], check=True)
    os.chdir("..")

@op
def run_yolo_enrichment():
    subprocess.run(["python", "src/yolo_detect.py"], check=True)
    # Run dbt again to include enrichments
    os.chdir("medical_warehouse")
    subprocess.run(["dbt", "run", "--models", "marts.fct_image_detections"], check=True)
    os.chdir("..")

@job
def full_pipeline():
    load_raw_to_postgres(scrape_telegram_data())
    run_yolo_enrichment(run_dbt_transformations(load_raw_to_postgres()))

# Schedule daily at 00:00
daily_schedule = ScheduleDefinition(
    job=full_pipeline,
    cron_schedule="0 0 * * *"
)

@repository
def my_repo():
    return [full_pipeline, daily_schedule]