# CLUTCH XI: Dataset Architecture & Data Validation Report

**Project:** CLUTCH XI — Rajasthan Royals SupeRR Selector Season 2  
**Document Type:** Dataset Specification & Quality Audit  
**Status:** Audited & Verified  

---

## 1. Dataset Schema and Overview

The CLUTCH XI modeling architecture operates directly on the official **Rajasthan Royals Data Pack**, encompassing professional T20 cricket from 2022 to 2026.

```
+-------------------------------------------------------------------------------------------------------+
| DATA PACK TABLES SUMMARY                                                                              |
+----------------------------------+------------+-------------+-----------------------------------------+
| Table Name                       | Total Rows | Total Cols  | Entity Description                      |
+----------------------------------+------------+-------------+-----------------------------------------+
| competitions.csv                 | 141        | 4           | Competition names, formats, seasons     |
| teams.csv                        | 353        | 3           | Team names and abbreviations            |
| matches.csv                      | 883        | 22          | Match metadata, venues, toss, results   |
| playing_eleven.csv               | 28,381     | 9           | Match lineups, captains, wicketkeepers  |
| competition_team_player_mapping  | 6,413      | 6           | Player-team-tournament roster mapping   |
| ball_by_ball.csv                 | 200,999    | 33          | Granular ball-by-ball delivery log      |
+----------------------------------+------------+-------------+-----------------------------------------+
```

### Relational Schema & Linkages:
- `ball_by_ball.match_id` $\rightarrow$ `matches.match_id`
- `ball_by_ball.striker_id`, `bowler_id` $\rightarrow$ `playing_eleven.player_id`
- `matches.competition_id` $\rightarrow$ `competitions.competition_id`
- `matches.home_team_id`, `away_team_id` $\rightarrow$ `teams.team_id`
- **Primary Key Integrity:** All primary keys in `matches` (883 unique IDs) and `competitions` (141 unique IDs) are strictly unique with zero duplicate rows.

---

## 2. Ball-by-Ball Cricket Definitions

Through forensic empirical validation across all 200,999 deliveries, column meanings were established from direct game evidence rather than naming assumptions:

### 2.1 The Meaning of `runs` vs `extras`
- **`runs`:** Represents **batter runs off the bat only**. It does NOT include extras. For example, when a wide is bowled with no bat contact, `runs = 0` and `extras1_runs = 1`.
- **`extras1_runs`:** Represents the primary penalty run awarded for delivery extras (wides, no-balls).
- **`extras_2_runs`:** Represents secondary extras conceded during the delivery (e.g. overthrows, byes).
- **Total Delivery Runs:** Evaluated strictly as $\text{runs} + \text{extras1\_runs} + \text{extras\_2\_runs}$.

### 2.2 Extras Types and Legal Deliveries
The dataset contains 5 distinct values in `extras_type`:
1. `NaN` (189,167 deliveries): Clean delivery off the bat. Legal ball.
2. `wide` (6,957 deliveries): Wide delivery. **Illegal delivery.** Excluded from batter balls faced; excluded from bowler legal balls.
3. `legbyes` (2,686 deliveries): Leg-bye off batter pads. Legal ball. Excluded from bowler runs conceded.
4. `byes` (1,232 deliveries): Bye past wicketkeeper. Legal ball. Excluded from bowler runs conceded.
5. `Overstep` (866 deliveries): Front-foot no-ball. **Illegal delivery.** Counts as batter ball faced; excluded from bowler legal balls.
6. `other` (91 deliveries): Other no-balls (waist-high full toss, fielding restriction violation). **Illegal delivery.**

### 2.3 Bowler Runs Conceded
In strict adherence to ICC Playing Conditions and MCC Law 21:
$$\text{Bowler Runs Conceded} = \text{runs} + \text{wides} + \text{no\_balls}$$
Fielding extras (`byes` and `legbyes`) are team penalties that are **not credited against the bowler's individual figures**.

### 2.4 Wickets and Dismissal Types
The dataset records 10,881 dismissals (`is_wicket = 1`):
- **Bowler-Credited Wickets (9,926 dismissals):** `caught` (6,912), `bowled` (1,714), `lbw` (926), `stumped` (361), `hit wicket` (13).
- **Non-Bowler Wickets (955 dismissals):** `run out` (951), `retired out` (3), `obstructing the field` (1).
- **Non-Striker Runouts:** The engine correctly identifies runouts where the dismissed player is the non-striker (`is_non_striker_out`), crediting the dismissal to the non-striker and ensuring the striker's wicket count remains accurate.

---

## 3. Match and Innings Structure

Across the 883 matches:
- **Total Innings Bowl Records:** 1,732 innings.
- **Innings 1 & 2:** Standard target-setting and chasing innings.
- **Innings 3 & 4 (Super Overs):** Exactly 4 innings belonging to 2 tied matches:
  - Match 48679 (Delhi Capitals vs Kings XI Punjab): Tied, Super Over played.
  - Match 48721 (Sunrisers Hyderabad vs Kolkata Knight Riders): Tied, Super Over played.
  These deliveries are dual-verified and assigned a baseline pressure of $100.0$.

---

## 4. Resolution of Revised Targets & Rain-Affected Matches

### 4.1 Match 48610 (Sri Lanka vs England, 27 October 2018)
- **Raw Match Metadata:** `revised_target = 115.0`, `revised_overs = 16.0`, `result = "England Won by 11 runs (DLS method)"`.
- **Raw Delivery Sequence:**
  - Innings 1: England batted first, scoring **187/8** in 20.0 overs (120 legal balls).
  - Innings 2: Sri Lanka batted second, scoring **125/4** in 15.0 overs (90 legal balls) when rain stopped play.
- **Mathematical Reconciliation:**
  $$\text{Sri Lanka Actual Score} = 125 \text{ runs in } 15.0 \text{ overs}$$
  $$\text{England Winning Margin} = 11 \text{ runs}$$
  $$\mathbf{\text{DLS Par Score}} = 125 + 11 = \mathbf{136 \text{ runs}}$$
  $$\mathbf{\text{Inferred Winning Target}} = 136 + 1 = \mathbf{137 \text{ runs}}$$
- **Audit Conclusion:** The recorded value `115.0` was an erroneous data entry (if the target were 115, Sri Lanka would have won by 10 runs). Setting `revised_target = 137.0` is an **external inference** required to resolve this contradiction.

### 4.2 Four Pre-Shortened Matches
Four matches in the dataset had both innings scheduled for fewer than 20 overs due to pre-match rain delays:
1. **Match 15795:** Scheduled for 14.0 overs (84 legal balls).
2. **Match 23674:** Scheduled for 19.0 overs (114 legal balls).
3. **Match 31278:** Scheduled for 17.0 overs (102 legal balls).
4. **Match 48514:** Scheduled for 17.0 overs (102 legal balls).

The engine dynamically sets scheduled legal balls to the actual scheduled length ($N_{\text{overs}} \times 6$), ensuring phase progression, death-over urgency, and expected wickets are scale-invariant.
