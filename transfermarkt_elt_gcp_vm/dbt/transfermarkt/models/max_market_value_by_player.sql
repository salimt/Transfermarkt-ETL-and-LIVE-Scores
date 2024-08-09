
-- This model retrieves the player ID, full name, highest market value date,
-- and the date it was recorded. It is used to analyze the highest market value

SELECT
  DISTINCT p.player_id,
  p.full_name,
  mv.HighestMarketValue,
  mv.HighestMarketValueDate
FROM
  `transfermarkt_analytics.profiles` p
JOIN
  `transfermarkt_analytics.market_value_history` mv
ON
  p.player_id = mv.player_id
ORDER BY
  mv.HighestMarketValue DESC
LIMIT
  50
