WITH player_stats AS (
    SELECT
        p.player_id,
        p.full_name,
        p.Position,
        p.club,
        p.league,
        ARRAY_AGG(DISTINCT COALESCE(mvh.Club, 'Unknown')) AS club_list,
        COUNT(DISTINCT COALESCE(mvh.Club, 'Unknown')) AS num_clubs,
        AVG(COALESCE(mvh.MarketValueAmount, 0)) AS avg_market_value,
        MAX(COALESCE(mvh.MarketValueAmount, 0)) AS max_market_value,
        MIN(COALESCE(mvh.MarketValueAmount, 0)) AS min_market_value
    FROM
        `transfermarkt_analytics.profiles`  p
    LEFT JOIN
        `transfermarkt_analytics.market_value_history` mvh ON p.player_id = mvh.player_id
    GROUP BY
        p.player_id, p.full_name, p.Position, p.club, p.league
)

SELECT
    *,
    CASE
        WHEN avg_market_value >= 10000000 THEN 'High Value Player'
        WHEN avg_market_value >= 5000000 THEN 'Medium Value Player'
        ELSE 'Low Value Player'
    END AS player_value_category
FROM
    player_stats
ORDER BY
    avg_market_value DESC