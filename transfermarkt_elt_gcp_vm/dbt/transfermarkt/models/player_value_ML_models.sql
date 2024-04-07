WITH
linear_regression_predictions AS (
  SELECT
    player_id,
    full_name,
    MarketValueAmount as current_market_value,
    predicted_MarketValueAmount as predicted_value_linear_regression
  FROM ML.PREDICT(MODEL `parma-data-elt.transfermarkt_analytics.player_market_value_linear_regression`,
    (SELECT player_id, full_name, MarketValueAmount FROM `transfermarkt_analytics.market_value_history` WHERE MarketValueAmount IS NOT NULL))
),
arima_plus_predictions AS (
  SELECT
    player_id,
    full_name,
    MarketValueAmount as current_market_value,
    predicted_MarketValueAmount as predicted_value_arima_plus
  FROM ML.PREDICT(MODEL `parma-data-elt.transfermarkt_analytics.player_market_value_arima_plus`,
    (SELECT player_id, full_name, MarketValueAmount FROM `transfermarkt_analytics.market_value_history` WHERE MarketValueAmount IS NOT NULL))
),
-- xgboost_predictions AS (
--   SELECT
--     player_id,
--     full_name,
--     MarketValueAmount as current_market_value,
--     predicted_MarketValueAmount as predicted_value_xgboost
--   FROM ML.PREDICT(MODEL `parma-data-elt.transfermarkt_analytics.player_market_value_xgboost`,
--     (SELECT player_id, full_name, MarketValueAmount FROM `transfermarkt_analytics.market_value_history` WHERE MarketValueAmount IS NOT NULL))
-- )

SELECT
  linear_regression_predictions.player_id,
  linear_regression_predictions.full_name,
  linear_regression_predictions.current_market_value,
  linear_regression_predictions.predicted_value_linear_regression,
  arima_plus_predictions.predicted_value_arima_plus,
  -- xgboost_predictions.predicted_value_xgboost
FROM
  linear_regression_predictions
JOIN
  arima_plus_predictions
ON
  linear_regression_predictions.player_id = arima_plus_predictions.player_id
-- JOIN
--   xgboost_predictions
-- ON
--   linear_regression_predictions.player_id = xgboost_predictions.player_id
ORDER BY
  linear_regression_predictions.current_market_value DESC
LIMIT 
  1000