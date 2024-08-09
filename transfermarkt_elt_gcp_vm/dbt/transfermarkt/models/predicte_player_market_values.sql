WITH top_1000_players AS (
    SELECT
        player_id,
        full_name,
        MarketValueAmount,
        predicted_value.predicted_MarketValueAmount
    FROM
        `transfermarkt_analytics.market_value_history` mvh
    JOIN
        `transfermarkt_analytics.profiles` p ON mvh.player_id = p.player_id
    JOIN
        `transfermarkt_analytics.players_stats` ps ON mvh.player_id = ps.Player_ID
    CROSS JOIN
        UNNEST(
            ML.PREDICT(MODEL `parma-data-elt.transfermarkt_analytics.player_market_value_linear_regression`, 
                STRUCT(
                    Age := DATE_DIFF(CURRENT_DATE(), p.date_of_birth, YEAR),
                    height := p.height,
                    club := p.club,
                    Caps := p.Caps,
                    Goals := p.Goals,
                    Appearances := ps.Appearances,
                    season_goals := ps.Goals,
                    Assists := ps.Assists,
                    Yellow_Cards := ps.Yellow_Cards,
                    Second_Yellow_Cards := ps.Second_Yellow_Cards,
                    Red_Cards := ps.Red_Cards,
                    Minutes := ps.Minutes,
                    num_seasons_played := (SELECT COUNT(DISTINCT Season) FROM `transfermarkt_analytics.players_stats` WHERE Player_ID = mvh.player_id),
                    market_value_month := EXTRACT(MONTH FROM mvh.Date),
                    market_value_year := EXTRACT(YEAR FROM mvh.Date)
                )
            )
        ) AS predicted_value
    WHERE mvh.MarketValueAmount IS NOT NULL
    ORDER BY MarketValueAmount DESC
    LIMIT 1000
)

SELECT
    player_id,
    full_name,
    MarketValueAmount,
    predicted_MarketValueAmount,
    MarketValueAmount - predicted_MarketValueAmount AS value_difference
FROM top_1000_players
ORDER BY value_difference ASC
LIMIT 100