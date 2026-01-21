-- Staging model for YOLO results
-- Cleans naming, types, removes invalid rows, adds basic business logic

WITH source AS (
    SELECT * FROM {{ source('raw', 'image_detections') }}
),

cleaned AS (
    SELECT
        message_id,
        channel_name,
        detected_class,
        confidence_score::double precision AS confidence_score,
        image_category,
        -- Simple quality flag (business rule)
        CASE 
            WHEN confidence_score >= 0.6 THEN 'high_confidence'
            WHEN confidence_score >= 0.4 THEN 'medium_confidence'
            ELSE 'low_confidence'
        END AS detection_quality
    FROM source
    WHERE 
        message_id IS NOT NULL
        AND image_category IS NOT NULL
        AND confidence_score BETWEEN 0 AND 1
)

SELECT * FROM cleaned