-- Enriched fact table joining messages + image detections

SELECT 
    f.message_id,
    f.channel_key,
    f.date_key,
    f.message_text,
    f.message_length,
    f.view_count,
    f.forward_count,
    f.has_image,
    -- Image enrichment (left join → null when no image/detection)
    i.detected_class,
    i.confidence_score,
    i.image_category,
    i.detection_quality
FROM {{ ref('fct_messages') }} f
LEFT JOIN {{ ref('stg_image_detections') }} i
    ON f.message_id = i.message_id
    -- If channel_name is needed for extra safety (optional)
    -- AND f.channel_name = i.channel_name