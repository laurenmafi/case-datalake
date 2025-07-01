SELECT 
  payment_type,
  COUNT(*) as count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM
  silver.nyc_tlc
GROUP BY payment_type
ORDER BY payment_type