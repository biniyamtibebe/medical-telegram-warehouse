SELECT
    i.message_id,
    c.channel_key,
    TO_CHAR(m.message_date, 'YYYYMMDD')::INT AS date_key,
    i.detected_class,
    i.confidence_score,
    i.image_category
FROM raw.image_detections i
JOIN {{ ref('fct_messages') }} m ON i.message_id = m.message_id AND i.channel_name = m.channel_name  -- Adjust if needed
JOIN {{ ref('dim_channels') }} c ON i.channel_name = c.channel_name