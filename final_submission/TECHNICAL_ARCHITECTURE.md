# CLUTCH XI: Technical Architecture & System Pipeline

**Project:** CLUTCH XI — Rajasthan Royals SupeRR Selector Season 2  
**Document Type:** Technical Architecture Specification  
**Status:** Audited & Verified  

---

## 1. System Pipeline Overview

The CLUTCH XI architecture is implemented as an end-to-end, deterministic data pipeline in Python. The system converts raw, unstructured delivery records into standardized situational player intelligence through eight sequential stages:

```
+---------------------------------------------------------------------------------------------------+
| CLUTCH XI DATA PROCESSING PIPELINE                                                                |
+---------------------------------------------------------------------------------------------------+
|  1. INGESTION & DATA CLEANING                                                                     |
|     Load 6 relational tables; apply strict cricket law rules (extras, balls faced, wickets).      |
+---------------------------------------------------------------------------------------------------+
                                  |
                                  v
+---------------------------------------------------------------------------------------------------+
|  2. PRE-DELIVERY STATE RECONSTRUCTION                                                             |
|     Compute state vector (runs_before, wickets_before, balls_before, CRR, RRR) strictly prior     |
|     to ball outcome (Zero Data Leakage). Scale scheduled lengths for shortened matches.           |
+---------------------------------------------------------------------------------------------------+
                                  |
                                  v
+---------------------------------------------------------------------------------------------------+
|  3. DYNAMIC PRESSURE ENGINE                                                                       |
|     Calculate continuous pressure score (0.0 to 100.0) for every ball. Apply death acceleration,  |
|     wicket crisis, chase leverage, and post-win / blowout dampeners.                              |
+---------------------------------------------------------------------------------------------------+
                                  |
                                  v
+---------------------------------------------------------------------------------------------------+
|  4. HIGH-PRESSURE SUBSETTING & AGGREGATION                                                        |
|     Filter high-pressure balls (P >= 50.0). Compute batter and bowler aggregates across overall,  |
|     pressure, and extreme pressure (P >= 75.0) tiers.                                             |
+---------------------------------------------------------------------------------------------------+
                                  |
                                  v
+---------------------------------------------------------------------------------------------------+
|  5. BAYESIAN SHRINKAGE & CONJUGATE PRIORS                                                         |
|     Shrink strike rates (K=30 balls), economy rates (K=36 balls), and batting average via         |
|     conjugate prior (K=5 outs) to eliminate zero-dismissal singularities.                         |
+---------------------------------------------------------------------------------------------------+
                                  |
                                  v
+---------------------------------------------------------------------------------------------------+
|  6. CONFIDENCE-WEIGHTED 70/30 FORMAT BLENDING                                                     |
|     Calculate sample confidence C_IPL and C_T20I. Dynamically blend IPL and T20I performances;    |
|     apply environmental par normalization and 10% T20I calibration factor.                        |
+---------------------------------------------------------------------------------------------------+
                                  |
                                  v
+---------------------------------------------------------------------------------------------------+
|  7. COMPOSITE Z-SCORE STANDARDIZATION & PERCENTILE PROJECTION                                     |
|     Calculate 7-component standardized composite score (weights sum to 1.00). Map to percentile   |
|     via normal CDF Phi(Z); scale by overall sample confidence.                                    |
+---------------------------------------------------------------------------------------------------+
                                  |
                                  v
+---------------------------------------------------------------------------------------------------+
|  8. DELIVERABLE EXPORT & VALIDATION CHECKS                                                        |
|     Generate Top 10 Batters, Top 10 Bowlers, All Player Scores, Performance Summary, and execute  |
|     6 automated unit tests.                                                                       |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Component Specifications

### 2.1 Module 1: `src/model_pressure.py`
- **Primary Responsibility:** Data ingestion, delivery ordering, pre-delivery state reconstruction, and delivery pressure scoring.
- **Key Inputs:** `Data Pack/ball_by_ball.csv`, `Data Pack/matches.csv`, `Data Pack/competitions.csv`.
- **Key Outputs:** In-memory DataFrame `bbb_df` with appended columns:
  - `batting_pressure`: Continuous score $[0.0, 100.0]$
  - `bowling_pressure`: Continuous score $[0.0, 100.0]$
  - `batting_tier`, `bowling_tier`: Categorical tiers (Low, Medium, High, Extreme)
  - `scheduled_balls_inn1`, `scheduled_balls_inn2`: Dynamic innings lengths
  - `is_target_reliable`: Target validity boolean flag

### 2.2 Module 2: `src/clutch_engine.py`
- **Primary Responsibility:** Player-level aggregations, Bayesian shrinkage, format blending, composite scoring, and final ranking generation.
- **Key Inputs:** `bbb_df` from `model_pressure.py`.
- **Key Outputs:**
  - `output/Top_10_Batters.csv`
  - `output/Top_10_Bowlers.csv`
  - `output/All_Player_Scores.csv`
  - `output/Player_Performance_Summary.csv`
  - `output/Pressure_Delivery_Analysis.csv`

### 2.3 Module 3: `output/Dashboard/app.py`
- **Primary Responsibility:** Interactive visual analytics interface built with Streamlit and Plotly.
- **Key Features:**
  - Dynamic KPI cards and executive briefing tabs.
  - Interactive scatter plots (Resilience Delta vs. Strike Rate, Economy vs. Wickets Per Over).
  - Searchable 958-player database explorer.
  - Rajasthan Royals IPL 2027 Auction Intelligence recommendations.

---

## 3. Data Integrity & Verification Architecture

```
+---------------------------------------------------------------------------------------------------+
| AUTOMATED SANITY AND UNIT TEST SUITE                                                              |
+--------------------------+----------------------------------------------------+-------------------+
| Test Identifier          | Verification Condition                             | Execution Status  |
+--------------------------+----------------------------------------------------+-------------------+
| TEST 1 (Wide Exclusion)  | Wide deliveries excluded from batter balls faced   | PASSED            |
| TEST 2 (Byes Exclusion)  | Byes & leg-byes excluded from bowler runs conceded | PASSED            |
| TEST 3 (Runout Exclusion)| Runouts excluded from bowler wickets               | PASSED            |
| TEST 4 (Non-Striker Out) | Non-striker runouts credited to non-striker only   | PASSED            |
| TEST 5 (Zero Leakage)    | Pre-delivery state vector strictly precedes ball   | PASSED            |
| TEST 6 (Rank Uniqueness) | Exactly 10 unique players in both Top 10 lists     | PASSED            |
+--------------------------+----------------------------------------------------+-------------------+
```

### Determinism and Reproducibility:
- Zero stochastic or random seed dependencies.
- Pipeline execution produces identical numerical outputs on every run across all platforms.
