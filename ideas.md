# Shiptivity: Kanban Board Analysis and Ideas to Grow Daily Active Users

Kanban Board released **2018-06-02**. Data: logins 2018-02-03 to 2019-02-01, card history 2018-06-02 to 2019-02-01 (UTC).
SQL: `answer.sql`. Charts: `chart_daily_active_users.png`, `chart_status_changes_by_card.png`.

## What the data says

| Finding | Number |
|---|---|
| Average daily active users (DAU), before release (119 days) | **3.35** |
| Average DAU, after release (245 days) | **11.79** (+252%) |
| Tighter window: 4 weeks before vs 4 weeks after | 5.79 vs 12.25 (+112%) |
| DAU in July 2018 (post-launch peak) vs last 30 days | 12.9 vs 10.0 (-22%) |
| Real status changes recorded (card creations excluded) | 286 |
| Cards that never moved | 38 of 200 (19%) |
| Cards with exactly 2 moves (backlog > in progress > complete) | 100 |
| In-progress cards that have sat more than 30 days | 37 of 58 (64%) |
| Backlog cards older than 30 days | 40 of 44 |
| Users with no login in the last 30 days | 22 of 99 (22%) |
| Monthly active users (last 30 days) / DAU | 78 / 10.0 (about 13% daily stickiness) |
| Median post-launch user active on | 20 of 245 days |
| Backward moves (in progress > backlog, complete > in progress) | 16 of 286 (6%) |

**Reading it honestly**

- The jump in DAU is real and large, but not all of it is the feature. DAU was already climbing before release (about 1 in Feb, 5.5 in May), and only 38 users logged in before release versus 99 after, so user-base growth is mixed in. The fairer estimate is "roughly doubled", not 3.5x.
- DAU has drifted down since July while card moves keep rising (47 in Dec, 149 in Jan). The people using the board are using it more, but fewer people show up on a given day.
- Cards stall: average wait is about 66 days from creation to first move, and about 35 days from start to finish.

## Idea 1: Aging cards and stale-card nudges

**Hypothesis.** Cards stall because nothing makes a stale card visible. 64% of in-progress cards have sat more than 30 days and 19% of cards were never moved. If we show how long a card has been in its lane and prompt users when a card passes a threshold, more cards will get moved, and each prompt gives a user a reason to log in.

**Expected impact.** Cut the share of in-progress cards older than 30 days from 64% to under 40%, and lift weekly status changes by 20-30%. This directly supports the ticket goal of 15% more tasks marked done. DAU effect: roughly +0.5 to +1.0 (5-10%), assuming the nudges bring back a handful of existing users each week. To be validated with an A/B test.

**What the feature is.** Each card shows a small "age in lane" badge (for example "42d") that turns amber after 14 days and red after 30. A banner at the top of the board says "5 cards haven't moved in 30+ days" and filters to them in one click. Optional email/in-app prompt: "Is this still in progress?" with one-tap buttons to move it to Complete or back to Backlog.

```
[Backlog]            [In Progress]          [Complete]
 Card A  (12d)        Card D  (42d) RED      Card G
 Card B  (95d) RED    Card E  (9d)           Card H
 5 cards stale  >  [Show stale]
```

## Idea 2: Weekly board digest email, including a win-back for lapsed users

**Hypothesis.** Users lapse because there is no trigger to come back. 22 of 99 post-launch users (22%) have not logged in for 30+ days, and DAU is down 22% from its July peak. A weekly digest that summarizes the state of the board will bring lapsed users back and add visits from active ones.

**Expected impact.** Return DAU from 10.0 to roughly 11.2 (+12%). Arithmetic: win back about 5 of the 22 lapsed users (about 25%) at roughly 0.08 DAU each is +0.4. If 30% of the 78 monthly users add one extra active day per month, that is about +0.8. Total about +1.2 DAU. Measure by comparing digest recipients against a holdout group.

**What the feature is.** A weekly email (Monday) per user: "This week on your board: 3 moved to Complete, 4 cards stuck in progress, 2 new in Backlog", with deep links to the stale cards. Users inactive for 30+ days get a win-back variant that leads with what is waiting. Includes an unsubscribe and frequency setting.

```
Subject: 4 cards are stuck in progress
  Completed this week: 3      New: 2
  Stuck > 30 days:  Card D, Card F, Card K
  [Open your board]
```

## Idea 3: Assign cards to teammates, with notifications

**Hypothesis.** The board is single-player: cards have no owner, so one person's activity does not pull anyone else back in. Only 13% of monthly users are active on a given day, and the median user shows up on about 20 of 245 days. If a card can be assigned to a teammate who is notified, each assignment gives that person a concrete reason to log in.

**Expected impact.** If about 15 existing users are pulled in once every two weeks by an assignment, that is about +1.1 DAU (+11%). It also gives us per-user attribution for card moves, which we cannot measure today. A/B test with assignment enabled for half of accounts.

**What the feature is.** An "Assignee" avatar on each card. Assigning a card, or moving a card you own, sends an in-app and email notification ("Dana assigned you Card D"). A "My cards" filter on the board shows only your assignments.

```
+----------------------+
| Card D            (DP)|  <- assignee avatar
| In progress, 9d       |
+----------------------+
 Notification: "Dana assigned you Card D"  [Open]
```

## Before we build: data gaps worth fixing

1. `card_change_history` has no `user_id`, so we cannot say who moved a card or link card moves to logins.
2. Reorders within a lane are not recorded (every one of the 286 rows is a status change), so we cannot measure the priority-ordering part of the feature.
3. 200 of 486 history rows are card creations (`oldStatus IS NULL`). All card-move queries exclude them.
4. All dates are UTC. The first login day (2018-02-03) is a partial day.
