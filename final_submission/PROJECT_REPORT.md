# CLUTCH XI: Advanced Situational Pressure Intelligence & Player Valuation

**Rajasthan Royals — SupeRR Selector Season 2 | Round 1 Submission**  
**Role:** Senior Cricket Data Scientist & Quantitative Modeling Group  
**Status:** Audited & Submission Ready  
**Submission Package:** [final_submission/](file:///c:/Users/HP/Contacts/Desktop/dbms%20documentation/final_submission)  

---

## 1. Executive Summary

Traditional T20 analytics rely heavily on volume-accumulated metrics: career batting averages, overall strike rates, and raw economy rates. However, modern franchise cricket and tournament championships are decided in high-leverage inflection points: defending 12 off the final over, halting a collapse at 30/3, or scoring 48 off the last 18 balls. Conventional statistics treat a boundary scored in a dead rubber identically to a boundary struck when chasing 12 an over against elite death bowling.

**CLUTCH XI** is an end-to-end quantitative analytics engine built on the proprietary Rajasthan Royals dataset of **200,999 deliveries across 883 T20 matches (2022–2026)** spanning the Indian Premier League (IPL) and Men's T20 Internationals (T20I).

The system addresses the fundamental question:
> *"Which players consistently maintain or elevate their performance when match situations become difficult, and who represents the most reliable investment for high-leverage moments?"*

### Core Architectural Pillars:
1. **Dynamic Pre-Delivery Pressure Model:** Evaluates situational stress on a scale of $0.0$ to $100.0$ for every delivery prior to the ball being bowled, incorporating required run rate stress, wicket scarcity, match phase progression, death-over urgency, and score deficits.
2. **Strict Cricket Law Compliance:** Differentiates batter balls faced (including no-balls, excluding wides) from bowler legal deliveries (excluding wides and no-balls). Excludes fielding extras (byes, leg-byes) from bowler runs conceded and runouts from bowler wickets.
3. **Bayesian Shrinkage & Conjugate Priors:** Solves small-sample volatility and the zero-dismissal singularity ($K_{\text{outs}} = 5.0$) through empirical Bayes shrinkage towards format-specific population benchmarks.
4. **Confidence-Weighted Format Blending:** Unifies IPL and T20I performances via a sample-proportional 70/30 weighting framework with environmental normalization and an empirical competition calibration discount.
5. **Multi-Faceted Composite Scoring:** Evaluates performance across 7 distinct dimensions (rate metrics, expectation-adjusted resilience deltas, boundary/dot differentials, extreme pressure performance, and multi-season consistency).

---

## 2. Official Unstop Submission Rankings

### 2.1 Top 10 Batters Under Pressure

| Rank | Player Name | Player ID | Clutch Rating | Pressure SR | Extreme SR | Pressure Avg | Pressure Balls | IPL Balls | Matches | Strategic Tactical Role |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | **Jos Buttler** | 813 | **96.81** | 181.35 | 237.93 | 45.70 | 252 | 173 | 16 | Primary Chase Master & High-Leverage Opener |
| **2** | **Ashutosh Sharma** | 8101 | **94.72** | 177.31 | 192.22 | 28.13 | 238 | 232 | 20 | Lower-Order Death Finisher & Boundary Enforcer (#7/#8) |
| **3** | **Tim David** | 6396 | **92.68** | 186.55 | 195.39 | 36.31 | 446 | 293 | 46 | Primary Death-Overs Closer (#6) |
| **4** | **Dinesh Karthik** | 143 | **91.99** | 186.12 | 168.29 | 38.80 | 209 | 171 | 22 | Veteran Finisher & Designated Specialist |
| **5** | **Namboori Tilak Varma** | 7897 | **90.22** | 155.28 | 188.89 | 56.60 | 729 | 469 | 53 | Middle-Order Anchor & Crisis Stabilizer (#4) |
| **6** | **Rachin Ravindra** | 4854 | **89.96** | 172.88 | 143.48 | 34.00 | 118 | 55 | 12 | Dynamic Top-Order Floater (#3) & Spin Option |
| **7** | **Glenn Maxwell** | 838 | **89.04** | 175.92 | 223.53 | 30.63 | 245 | 114 | 21 | Counter-Attacking Middle-Overs Weapon (#4/#5) |
| **8** | **George Linde** | 4229 | **85.63** | 173.49 | 195.45 | 28.80 | 83 | 9 | 9 | Lower-Order Hitting All-Rounder (#7/#8) |
| **9** | **Reeza Hendricks** | 768 | **85.43** | 167.03 | 142.86 | 77.25 | 185 | 0 | 11 | High-Floor Top-Order Anchor (T20I Specialist) |
| **10** | **Babar Azam** | 2485 | **85.22** | 183.53 | 218.18 | 52.00 | 85 | 0 | 8 | Top-Order Anchor & Number 3 Stabilizer |

### 2.2 Top 10 Bowlers Under Pressure

| Rank | Player Name | Player ID | Clutch Rating | Pressure Econ | Extreme Econ | Pressure WPO | Pressure Overs | IPL Overs | Wickets | Strategic Tactical Role |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | **Sunil Narine** | 781 | **91.69** | 6.95 | 7.43 | 0.269 | 126.3 | 126.3 | 34 | Middle-Overs Choke Engine & Powerplay Option |
| **2** | **Riley Meredith** | 5940 | **86.99** | 8.45 | 7.33 | 0.436 | 18.2 | 18.2 | 8 | Middle/Death Express Pace Enforcer (145kph+) |
| **3** | **Liam Dawson** | 722 | **86.40** | 5.77 | 7.33 | 0.412 | 21.5 | 0.0 | 9 | Powerplay & Middle Containment Finger Spinner |
| **4** | **Mitchell Santner** | 4101 | **85.91** | 7.32 | 6.97 | 0.344 | 159.5 | 55.1 | 55 | High-Control Finger Spinner & Batting Option (#8) |
| **5** | **Sufiyan Muqeem** | 34485 | **84.77** | 5.07 | 5.60 | 0.401 | 47.2 | 0.0 | 19 | Mystery Wrist Spinner & Middle-Overs Wicket-Taker |
| **6** | **Mark Wood** | 2985 | **84.61** | 8.70 | 6.60 | 0.626 | 30.2 | 12.0 | 19 | Express Strike Bowler (9.58 balls/wicket) |
| **7** | **Rashid Khan** | 4722 | **84.09** | 7.45 | 7.56 | 0.350 | 222.4 | 128.3 | 78 | Primary Match-Winning Leg-Spinner |
| **8** | **Mohammad Nawaz** | 2490 | **83.50** | 6.81 | 7.50 | 0.410 | 92.4 | 0.0 | 38 | High-Leverage Finger Spinner & Match Matchup Weapon |
| **9** | **Lungi Ngidi** | 4641 | **83.38** | 8.65 | 5.00 | 0.377 | 74.2 | 29.5 | 28 | Hit-the-Deck Death Overs Strike Seamer |
| **10** | **Maheesh Theekshana** | 19316 | **83.02** | 7.45 | 7.50 | 0.241 | 170.1 | 64.0 | 41 | Powerplay & Death Carrom Ball Specialist |

---

## 3. Key Tactical Insights for Rajasthan Royals (RR)

### Insight 1: Jos Buttler is the Undisputed World-Leader in Pressure Chases
Jos Buttler achieves a Clutch Rating of **96.81**, the highest in the entire dataset. In high-pressure situations ($P \ge 50$), his strike rate accelerates from an already elite $155.39$ to **$181.35$**, and further soars to **$237.93$** under extreme pressure ($P \ge 75$). His pressure average of $45.70$ demonstrates that his boundary acceleration does not compromise his wicket preservation. Buttler is an indispensable cornerstone for championship-caliber squads.

### Insight 2: Ashutosh Sharma Represents the Highest-ROI Finishing Steal
Ranked #2 among all batters with a **94.72** Clutch Rating, Ashutosh Sharma faced 238 pressure balls almost entirely in the IPL ($w_{\text{IPL}} = 1.000$). His pressure strike rate of **$177.31$** and extreme pressure strike rate of **$192.22$** were achieved in catastrophic crisis scenarios coming in at #7/#8. In the mega-auction, Ashutosh represents an exceptional market inefficiency compared to high-priced established finishers.

### Insight 3: Sunil Narine Provides Incomparable Middle-Overs Squeeze
Sunil Narine leads all bowlers with a **91.69** Clutch Rating. Across 759 pressure balls ($126.3$ overs bowled under high stress), Narine conceded just **$6.95$ runs per over** while taking 34 wickets. Narine suppresses the opposition's scoring rate during the middle overs regardless of match state, drastically reducing the required run rate burden on the batting unit.

---

## 4. Verification and Compliance Summary

1. **Deterministic Execution:** The engine executes reproducibly across all environments.
2. **Zero Missing or Erroneous Data:** Across all 958 tracked players, the output tables contain exactly 0 NaN values, 0 infinite values, and 0 duplicate player records.
3. **Automated Unit Tests:** All cricket rule compliance tests (extras handling, non-striker runouts, overs calculation) pass with 100% success.
4. **Dataset Validation:** Match 48610 DLS target and pre-shortened match handling have been rigorously reconciled and documented based on empirical evidence.
