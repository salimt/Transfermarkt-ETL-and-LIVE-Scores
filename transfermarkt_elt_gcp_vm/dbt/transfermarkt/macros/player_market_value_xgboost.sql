{% macro create_bigquery_xgboost_model() %}
  {% set query %}
    CREATE OR REPLACE MODEL `transfermarkt_analytics.player_market_value_xgboost`
    OPTIONS(model_type='BOOSTED_TREE_REGRESSOR', input_label_cols=['MarketValueAmount']) AS
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
            APPROX_COUNT_DISTINCT(ps.Season) AS num_seasons_played,
            EXTRACT(MONTH FROM mvh.Date) AS market_value_month,
            EXTRACT(YEAR FROM mvh.Date) AS market_value_year,
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
            market_value_year
    )
    SELECT 
        player_id,
        full_name,
        MarketValueAmount,
        Age,
        height,
        club,
        Caps,
        Goals,
        Appearances,
        season_goals,
        Assists,
        Yellow_Cards,
        Second_Yellow_Cards,
        Red_Cards,
        Minutes,
        num_seasons_played,
        market_value_month,
        market_value_year
    FROM combined_data
  {% endset %}

  {% do adapter.execute(query) %}
{% endmacro %}