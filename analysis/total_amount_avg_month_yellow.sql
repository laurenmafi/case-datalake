SELECT
  dt AS `month`,
  ROUND(AVG(total_amount), 2) AS avg_total_amount
FROM
  silver.nyc_tlc
WHERE
  `source` = 'yellow'
GROUP BY
  dt
ORDER BY
  dt;
