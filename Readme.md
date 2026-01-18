# Medical Telegram Warehouse

End-to-end data pipeline extracting public Telegram medical/cosmetics channels in Ethiopia → raw data lake → PostgreSQL warehouse → dimensional model (star schema) → analytical API.

----

**Week 8 Challenge – 10 Academy AI Mastery**

## Architecture Overview

- **Extract**: Telethon scraper (`src/scraper.py`) → JSON + images
- **Load**: Raw JSON → PostgreSQL `raw.telegram_messages` (`src/load_to_postgres.py`)
- **Transform**: dbt (staging → marts star schema)
- **Enrich**: YOLOv8 object detection on images
- **Serve**: FastAPI analytical endpoints
- **Orchestrate**: Dagster pipeline

![High-level diagram] (you can add a simple draw.io / excalidraw diagram later)

----

## Project Structure
         medical-telegram-warehouse/
         ├── .env                      # secrets (not committed)
         ├── docker-compose.yml        # local PostgreSQL
         ├── requirements.txt
         ├── medical_warehouse/        # dbt project
         │   ├── dbt_project.yml
         │   ├── profiles.yml
         │   └── models/
         │       ├── staging/
         │       └── marts/
         ├── src/                      # python scripts
         ├── api/                      # FastAPI
         ├── data/                     # raw lake (gitignored)
         └── logs/

----

## Quick Start (Local Development)

1. Clone repo
2. Copy `.env.example` → `.env` and fill credentials
3. `docker-compose up -d` (starts PostgreSQL)
4. `pip install -r requirements.txt`
5. Scrape data: `python src/scraper.py`
6. Load to warehouse: `python src/load_to_postgres.py`
7. Transform & test: `cd medical_warehouse && dbt run && dbt test`
8. Generate docs: `dbt docs generate && dbt docs serve`
9. Run API: `uvicorn api.main:app --reload`
10. Run full pipeline: `dagster dev -f src/pipeline.py`

## Data Model (Star Schema)

- **Dimensions**: dim_channels, dim_dates
- **Fact**: fct_messages (+ fct_image_detections after YOLO)

See `dbt docs` for full lineage & descriptions.

## Security & Best Practices

- Credentials → `.env` + `.gitignore`
- No `.session` files in git
- Staging views, marts tables
- dbt tests + custom singular tests

## Next Steps / Known Limitations

- Add dbt seeds for channel metadata
- Fine-tune YOLO for medical products
- Add freshness checks
- Deploy Dagster + dbt Cloud / GitHub Actions

## Contributors

Biniyam – Week 8 Challenge