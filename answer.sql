-- TYPE YOUR SQL QUERY BELOW
-- Database: SQLite (sqlite3 ./shiptivity.db)
-- Feature release date (Kanban Board): 2018-06-02. All dates are UTC.

-- PART 1: Create a SQL query that maps out the daily average users before and after the feature change

-- 1a. Daily active users (distinct users who logged in) for EVERY calendar day,
--     labelled before/after the release. This is the series used for the line graph.
--     A calendar table is used so days with zero logins appear as 0 instead of being skipped
--     (skipping them would overstate the "before" average).
WITH RECURSIVE calendar(day) AS (
    SELECT DATE(MIN(login_timestamp), 'unixepoch') FROM login_history
    UNION ALL
    SELECT DATE(day, '+1 day')
    FROM calendar
    WHERE day < (SELECT DATE(MAX(login_timestamp), 'unixepoch') FROM login_history)
)
SELECT
    c.day,
    CASE WHEN c.day < '2018-06-02' THEN 'before' ELSE 'after' END AS period,
    COUNT(DISTINCT l.user_id) AS daily_active_users
FROM calendar c
LEFT JOIN login_history l
       ON DATE(l.login_timestamp, 'unixepoch') = c.day
GROUP BY c.day
ORDER BY c.day;

-- 1b. Average daily active users before vs after the release (the headline comparison).
WITH RECURSIVE calendar(day) AS (
    SELECT DATE(MIN(login_timestamp), 'unixepoch') FROM login_history
    UNION ALL
    SELECT DATE(day, '+1 day')
    FROM calendar
    WHERE day < (SELECT DATE(MAX(login_timestamp), 'unixepoch') FROM login_history)
),
daily AS (
    SELECT
        c.day,
        CASE WHEN c.day < '2018-06-02' THEN 'before' ELSE 'after' END AS period,
        COUNT(DISTINCT l.user_id) AS dau
    FROM calendar c
    LEFT JOIN login_history l
           ON DATE(l.login_timestamp, 'unixepoch') = c.day
    GROUP BY c.day
)
SELECT
    period,
    COUNT(*)                AS days_in_period,
    ROUND(AVG(dau), 2)      AS avg_daily_active_users,
    MIN(dau)                AS min_dau,
    MAX(dau)                AS max_dau
FROM daily
GROUP BY period
ORDER BY period DESC;   -- 'before' first, then 'after'


-- PART 2: Create a SQL query that indicates the number of status changes by card

-- NOTE: card_change_history also contains one row per card where oldStatus IS NULL.
-- That row is the card being CREATED, not a status change, so it is excluded.

-- 2a. Status changes per card (all 200 cards; cards that never moved show 0).
--     This is the series used for the "status changes by card" graph.
SELECT
    c.id   AS card_id,
    c.name AS card_name,
    COUNT(h.cardID) AS status_changes
FROM card c
LEFT JOIN card_change_history h
       ON h.cardID = c.id
      AND h.oldStatus IS NOT NULL
      AND h.oldStatus <> h.newStatus
GROUP BY c.id, c.name
ORDER BY status_changes DESC, c.id;

-- 2b. Distribution: how many cards had 0, 1, 2, ... status changes.
WITH per_card AS (
    SELECT c.id, COUNT(h.cardID) AS status_changes
    FROM card c
    LEFT JOIN card_change_history h
           ON h.cardID = c.id
          AND h.oldStatus IS NOT NULL
          AND h.oldStatus <> h.newStatus
    GROUP BY c.id
)
SELECT status_changes, COUNT(*) AS number_of_cards
FROM per_card
GROUP BY status_changes
ORDER BY status_changes;

-- 2c. Daily view: number of status changes per day, and how many distinct cards moved.
SELECT
    DATE(timestamp, 'unixepoch') AS day,
    COUNT(*)                     AS status_changes,
    COUNT(DISTINCT cardID)       AS cards_moved
FROM card_change_history
WHERE oldStatus IS NOT NULL
  AND oldStatus <> newStatus
GROUP BY day
ORDER BY day;

-- 2d. Daily status changes by card (one row per card per day it moved).
SELECT
    DATE(h.timestamp, 'unixepoch') AS day,
    h.cardID                       AS card_id,
    c.name                         AS card_name,
    COUNT(*)                       AS status_changes
FROM card_change_history h
JOIN card c ON c.id = h.cardID
WHERE h.oldStatus IS NOT NULL
  AND h.oldStatus <> h.newStatus
GROUP BY day, h.cardID, c.name
ORDER BY day, h.cardID;
