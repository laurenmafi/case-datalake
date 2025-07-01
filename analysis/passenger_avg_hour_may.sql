WITH CTE AS (
  SELECT 
    HOUR(pickup_datetime) as pickup_hour,
    DAY(pickup_datetime) as pickup_day,
    SUM(passenger_count) as sum_passengers
  FROM silver.nyc_tlc
  WHERE
    dt = '2023-05'
  GROUP BY 1, 2
)

SELECT
  pickup_hour,
  ROUND(AVG(sum_passengers), 2) AS avg_passenger_count
FROM
  CTE
GROUP BY
  pickup_hour
ORDER BY
  pickup_hour;
