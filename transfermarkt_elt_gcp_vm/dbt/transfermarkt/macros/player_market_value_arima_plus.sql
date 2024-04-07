{% macro create_bigquery_arima_plus_model() %}
  {% set query %}
    CREATE OR REPLACE MODEL `transfermarkt_analytics.player_market_value_arima_plus`
    OPTIONS(model_type='ARIMA_PLUS', time_series_timestamp_col='Date', time_series_data_col='MarketValueAmount', time_series_id_col='player_id', holiday_region='US') AS
    WITH combined_data AS (
        SELECT
            mvh.player_id,
            p.full_name,
            mvh.MarketValueAmount,
            DATE_DIFF(CURRENT_DATE(), p.date_of_birth, YEAR) AS Age,
            p.height,
            p.club,
            p.Caps,
            p.Goals,
            ps.Appearances,
            ps.Goals AS season_goals,
            ps.Assists,
            ps.Yellow_Cards,
            ps.Second_Yellow_Cards,
            ps.Red_Cards,
            ps.Minutes,
            COUNT(DISTINCT ps.Season) AS num_seasons_played,
            EXTRACT(MONTH FROM mvh.Date) AS market_value_month,
            EXTRACT(YEAR FROM mvh.Date) AS market_value_year,
            mvh.Date
        FROM
            `transfermarkt_analytics.market_value_history` mvh
        JOIN `transfermarkt_analytics.profiles` p ON mvh.player_id = p.player_id
        JOIN `transfermarkt_analytics.players_stats` ps ON mvh.player_id = ps.Player_ID
        WHERE mvh.MarketValueAmount IS NOT NULL
        GROUP BY
            mvh.player_id,
            p.full_name,
            mvh.MarketValueAmount,
            Age,
            p.height,
            p.club,
            p.Caps,
            p.Goals,
            ps.Appearances,
            ps.Goals,
            ps.Assists,
            ps.Yellow_Cards,
            ps.Second_Yellow_Cards,
            ps.Red_Cards,
            ps.Minutes,
            market_value_month,
            market_value_year,
            mvh.Date
    )
    SELECT 
      player_id, 
      Date, 
      MarketValueAmount
    FROM combined_data
  {% endset %}

  {% do adapter.execute(query) %}
{% endmacro %}