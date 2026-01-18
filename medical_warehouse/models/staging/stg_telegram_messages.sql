-- Clean and standardize raw data
WITH source AS (
    SELECT * FROM {{ source('raw', 'telegram_messages') }}
)

SELECT
    message_id,
    channel_name,
    CAST(message_date AS TIMESTAMP) AS message_date,
    message_text,
    has_media,
    views,
    forwards,
    image_path,
    LENGTH(message_text) AS message_length
FROM source
WHERE message_text IS NOT NULL AND message_date IS NOT NULL