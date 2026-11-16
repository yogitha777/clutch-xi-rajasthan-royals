# CLUTCH XI: Methodological Limitations, Assumptions & Future Roadmap

**Project:** CLUTCH XI — Rajasthan Royals SupeRR Selector Season 2  
**Document Type:** Risk Audit & Scientific Roadmap  
**Status:** Audited & Verified  

---

## 1. Executive Disclaimer on Model Scope

Senior data science auditing requires complete transparency regarding the boundaries and intended scope of the model:

> **IMPORTANT METHODOLOGICAL STATEMENT:**  
> The CLUTCH XI engine is a **situational player resilience and skill-execution scoring model**. It is designed to identify players who maintain or elevate their rate metrics and boundary/dot differentials when match stress is high.  
> **It does NOT predict actual match-winning probability, and does NOT claim to estimate true game-theoretic win expectancy.** Passing software execution tests and unit checks demonstrates deterministic code stability and internal mathematical consistency, but does not constitute external peer-reviewed scientific validation.

---

## 2. Comprehensive Accounting of Known Limitations

```
+-------------------------------------------------------------------------------------------------------+
| METHODOLOGICAL LIMITATIONS AUDIT                                                                      |
+--------------------------+-----------------------+-------------------------+--------------------------+
| Subsystem                | Current Implementation| Methodological Risk     | Production Solution      |
+--------------------------+-----------------------+-------------------------+--------------------------+
| Win Probability Proxy    | Logistic Heuristic    | Not trained on ball-by- | Machine learning win     |
|                          | balance proxy         | ball historical win rate| probability model (XGB)  |
+--------------------------+-----------------------+-------------------------+--------------------------+
| DLS Target Overrides     | External Inference    | Relies on hardcoded     | Integration of official  |
|                          | for Match 48610 (137) | exception patching      | ICC DLS resource tables  |
+--------------------------+-----------------------+-------------------------+--------------------------+
| Merged CSV Schema Quirk  | Merged DataFrame      | In All_Player_Scores:   | Explicit renaming to     |
|                          | suffix collisions     | pressure_balls_x and _y | bat_p_balls, bowl_p_balls|
+--------------------------+-----------------------+-------------------------+--------------------------+
| Shrinkage Priors         | Global fixed priors   | Fixed K parameters      | Hierarchical Bayesian    |
|                          | (e.g. K_sr = 30)      | across all player types | estimation via Stan/MCMC |
+--------------------------+-----------------------+-------------------------+--------------------------+
| Matchup Context          | Batter-bowler generic | Treats deliveries       | Ball-tracking & head-to- |
|                          | rate aggregates       | identically by tier     | head matchup adjustments |
+--------------------------+-----------------------+-------------------------+--------------------------+
```

### 2.1 Heuristic Win-Probability Proxy vs. Empirical Win Expectancy
In Innings 2, match leverage is calculated via the heuristic Chase Balance Proxy:
$$z = 1.25 \times \left(\frac{\text{wickets\_remaining}}{10.0}\right) - 0.25 \times (\text{RRR} - 8.92) - 0.35 \times (\text{Phase} - 0.5) - 1.0$$
While this logistic proxy is calibrated to cricket intuition (centered at par RRR $8.92$ and balancing wickets in hand against phase progression), it is **not** a predictive machine learning win-probability model trained on binary historical match outcomes. Consequently, leverage scores reflect situational urgency rather than true win-probability added (WPA).

### 2.2 External DLS Target Inferences
For Match 48610 (Sri Lanka vs. England, 2018), the target of $137$ is mathematically derived from the match result ($125 + 11 = 136$ par score $+ 1 = 137$ target). While this resolves a dataset contradiction where `revised_target` was incorrectly entered as $115.0$, it represents an **external domain inference** rather than an intrinsic data point in the Data Pack.

### 2.3 Fixed Hyperparameter Shrinkage
The Bayesian shrinkage parameters ($K_{\text{sr}} = 30$ balls, $K_{\text{outs}} = 5$ dismissals, $K_{\text{bowl}} = 36$ legal balls) are global empirical constants chosen via sensitivity analysis. While effective at dampening small-sample outliers, a fully hierarchical model would estimate separate variance components for each player role (top-order anchor vs. lower-order finisher).

### 2.4 Column Suffix Schema Quirk
In [`output/All_Player_Scores.csv`](file:///c:/Users/HP/Contacts/Desktop/dbms%20documentation/output/All_Player_Scores.csv), merging batting performance and bowling performance into a consolidated single-table format caused pandas suffix collisions:
- `pressure_balls_x` represents **batting pressure balls faced**.
- `pressure_balls_y` represents **bowling pressure legal balls bowled**.
While all underlying numbers and ranking outputs are mathematically unaffected, automated downstream ingestion scripts must recognize this naming distinction.

### 2.5 Unmodeled Contextual Variables
The current dataset lacks granular environmental features:
- **Pitch Conditions & Dew:** No variable tracks pitch degradation, turn, bounce, or the presence of evening dew.
- **Boundary Dimensions:** Ground-specific boundary lengths (e.g. short square boundaries at Chinnaswamy vs. large boundaries at MCG) are unrecorded.
- **Opposition Bowler Quality:** A boundary struck against Jasprit Bumrah is scored identically to a boundary struck against a part-time bowler in the same pressure tier.

---

## 3. Future Technical Roadmap

To advance the CLUTCH XI engine to an enterprise-grade franchise scouting platform, the following enhancements are planned:

### Phase 1: Machine Learning Win Probability Model (XGBoost / LightGBM)
- Train a gradient-boosted classification model on historical ball-by-ball states across 5,000+ global T20 matches.
- Replace the heuristic Chase Balance Proxy with calibrated Win Probability Added (WPA) and Leverage Index (pLI).

### Phase 2: Fully Hierarchical Bayesian Modeling (Stan / PyMC)
- Implement role-specific priors ($K$-factors conditional on batting position and bowling phase).
- Estimate player-specific skill variance across multi-year horizons using Markov Chain Monte Carlo (MCMC) sampling.

### Phase 3: Opposition Quality & Matchup Contextualization
- Integrate an Elo-based player rating system to weight every delivery by the quality of the opposing batter or bowler.
- Incorporate Hawkeye ball-tracking data (pitch map coordinates, release speeds, seam movement) to evaluate execution difficulty.

### Phase 4: Dynamic Auction Valuation Optimizer
- Couple the Clutch Rating with player salary data to calculate **Value Over Replacement Player (VORP)** under high-pressure scenarios, providing algorithmic bidding ceilings for the IPL mega-auction.
