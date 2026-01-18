-- Date dimension (generate dates dynamically)
{% set start_date = '2020-01-01' %}
{% set end_date = modules.datetime.date.today() %}

WITH dates AS (
    SELECT
        DATEADD(DAY, seq, '{{ start_date }}'::DATE) AS full_date
    FROM (
        SELECT ROW_NUMBER() OVER () - 1 AS seq
        FROM TABLE(GENERATOR(ROWCOUNT => DATEDIFF(DAY, '{{ start_date }}', '{{ end_date }}') + 1))
    )
)

SELECT
    TO_CHAR(full_date, 'YYYYMMDD')::INT AS date_key,
    full_date,
    DAYOFWEEK(full_date) AS day_of_week,
    TO_CHAR(full_date, 'Day') AS day_name,
    WEEKOFYEAR(full_date) AS week_of_year,
    MONTH(full_date) AS month,
    TO_CHAR(full_date, 'Month') AS month_name,
    QUARTER(full_date) AS quarter,
    YEAR(full_date) AS year,
    CASE WHEN DAYOFWEEK(full_date) IN (0, 6) THEN TRUE ELSE FALSE END AS is_weekend
FROM dates