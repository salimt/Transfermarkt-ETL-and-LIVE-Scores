WITH
linear_regression_evaluation AS (
  SELECT
    'linear_regression' as model,
    *
  FROM ML.EVALUATE(MODEL `parma-data-elt.transfermarkt_analytics.player_market_value_linear_regression`,
    (SELECT player_id, MarketValueAmount FROM `transfermarkt_analytics.market_value_history` WHERE MarketValueAmount IS NOT NULL))
),
arima_plus_evaluation AS (
  SELECT
    'arima_plus' as model,
    *
  FROM ML.EVALUATE(MODEL `parma-data-elt.transfermarkt_analytics.player_market_value_arima_plus`,
    (SELECT player_id, MarketValueAmount FROM `transfermarkt_analytics.market_value_history` WHERE MarketValueAmount IS NOT NULL))
),
xgboost_evaluation AS (
  SELECT
    'xgboost' as model,
    *
  FROM ML.EVALUATE(MODEL `parma-data-elt.transfermarkt_analytics.player_market_value_xgboost`,
    (SELECT player_id, MarketValueAmount FROM `transfermarkt_analytics.market_value_history` WHERE MarketValueAmount IS NOT NULL))
)

SELECT * FROM linear_regression_evaluation
UNION ALL
SELECT * FROM arima_plus_evaluation
UNION ALL
SELECT * FROM xgboost_evaluation