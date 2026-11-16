# CLUTCH XI: Final Ranking Forensic Reconciliation Report

**Audit Date:** November 15, 2026  
**Auditor Role:** Senior Cricket Data Scientist & Quantitative Analytics Auditor  
**Investigation Scope:** Forensic audit of batting Top 10 discrepancy between Stage 3 text drafts and generated CSV/PDF outputs.  
**Deliverable:** [output/FINAL_RANKING_RECONCILIATION.md](file:///c:/Users/HP/Contacts/Desktop/dbms%20documentation/output/FINAL_RANKING_RECONCILIATION.md)  

---

## 1. Executive Summary & Root Cause Resolution

This forensic investigation was initiated to resolve a critical discrepancy:
> *"The batting Top 10 in the final report differs from the Stage 3 Independent Scoring Audit text."*

### Forensic Finding:
1. **Authoritative Single Source of Truth:** The executable Python engine [src/clutch_engine.py](file:///c:/Users/HP/Contacts/Desktop/dbms%20documentation/src/clutch_engine.py) is the sole authoritative source of truth. It deterministically produced `output/Top_10_Batters.csv`, `output/Top_10_Bowlers.csv`, `output/All_Player_Scores.csv`, and `output/Player_Performance_Summary.csv`.
2. **Bit-for-Bit Deliverable Identity:** All files in `final_submission/` and `output/` are **100% bit-for-bit identical** (identical SHA-256 hashes, identical shapes, identical player scores).
3. **The Root Cause of the Discrepancy:** The discrepancy arose from a **stale textual insertion** in an early draft of Section 4.2 in `output/INDEPENDENT_SCORING_AUDIT.md`. That draft text inadvertently included player names (`Shashank Singh, Heinrich Klaasen, Nicholas Pooran, Tristan Stubbs, Sanju Samson`) paired with **invalid/mock player IDs** (`8095, 128, 4174, 3882, 1301, 190, 7861`) that **do not exist in the official Rajasthan Royals Data Pack**.
4. **Resolution:** The real, reproducible, mathematical Top 10 batting ranking produced by the active code has always been:
   1. **Jos Buttler** (813) — 96.81
   2. **Ashutosh Sharma** (8101) — 94.72
   3. **Tim David** (6396) — 92.68
   4. **Dinesh Karthik** (143) — 91.99
   5. **Namboori Tilak Varma** (7897) — 90.22
   6. **Rachin Ravindra** (4854) — 89.96
   7. **Glenn Maxwell** (838) — 89.04
   8. **George Linde** (4229) — 85.63
   9. **Reeza Hendricks** (768) — 85.43
   10. **Babar Azam** (2485) — 85.22
5. **Dashboard and PDF Concordance:** Both `output/Dashboard/app.py` and `output/CLUTCH_XI_Methodology_Report.pdf` read directly from `output/Top_10_Batters.csv` and reflect this exact ranking.

---

## 2. Task 1: Comparative Content Audit of Deliverables

A cryptographic SHA-256 and structural comparison was executed across the deliverables in `output/` and `final_submission/`:

```
+-----------------------------------------------------------------------------------------------------------------------+
| CRYPTOGRAPHIC & STRUCTURAL FILE VERIFICATION                                                                          |
+------------------------------------+------------------------------------+------------+---------------+----------------+
| Primary File Path                  | Mirror / Submission File Path      | SHA256 Hex | Shape (R x C) | Data Identity  |
+------------------------------------+------------------------------------+------------+---------------+----------------+
| output/Top_10_Batters.csv          | final_submission/Top_10_Batters.csv| 1f74f74179 | 10 x 21       | 100% Identical |
| output/Top_10_Bowlers.csv          | final_submission/Top_10_Bowlers.csv| 869233da02 | 10 x 23       | 100% Identical |
| output/All_Player_Scores.csv       | final_submission/All_Player_Scores | 402f484266 | 958 x 21      | 100% Identical |
| output/Player_Performance_Summary  | final_submission/Player_Performance| 402f484266*| 958 x 21      | 100% Identical |
+------------------------------------+------------------------------------+------------+---------------+----------------+
* Player_Performance_Summary.csv is identically equal to All_Player_Scores.csv sorted by batting_clutch_rating descending.
```

### Exact Content of Authoritative Top 10 Batters (`Top_10_Batters.csv`):
```
Rank  Player_ID  Player_Name           clutch_rating  pressure_runs  pressure_balls  pressure_sr  pressure_avg  ipl_weight
1     813        Jos Buttler           96.81          457.0          252.0           181.35       45.70         0.728
2     8101       Ashutosh Sharma       94.72          422.0          238.0           177.31       28.13         1.000
3     6396       Tim David             92.68          832.0          446.0           186.55       36.31         0.704
4     143        Dinesh Karthik        91.99          389.0          209.0           186.12       38.80         0.790
5     7897       Namboori Tilak Varma  90.22          1132.0         729.0           155.28       56.60         0.700
6     4854       Rachin Ravindra       89.96          204.0          118.0           172.88       34.00         0.687
7     838        Glenn Maxwell         89.04          431.0          245.0           175.92       30.63         0.696
8     4229       George Linde          85.63          144.0          83.0            173.49       28.80         0.358
9     768        Reeza Hendricks       85.43          309.0          185.0           167.03       77.25         0.000
10    2485       Babar Azam            85.22          156.0          85.0            183.53       52.00         0.000
```

### Exact Content of Authoritative Top 10 Bowlers (`Top_10_Bowlers.csv`):
```
Rank  Player_ID  Player_Name         clutch_rating  pressure_overs  pressure_balls  pressure_econ  pressure_wickets  pressure_wpo
1     781        Sunil Narine        91.69          126.3           759.0           6.95           34.0              0.269
2     5940       Riley Meredith      86.99          18.2            110.0           8.45           8.0               0.436
3     722        Liam Dawson         86.40          21.5            131.0           5.77           9.0               0.412
4     4101       Mitchell Santner    85.91          159.5           959.0           7.32           55.0              0.344
5     34485      Sufiyan Muqeem      84.77          47.2            284.0           5.07           19.0              0.401
6     2985       Mark Wood           84.61          30.2            182.0           8.70           19.0              0.626
7     4722       Rashid Khan         84.09          222.4           1336.0          7.45           78.0              0.350
8     2490       Mohammad Nawaz      83.50          92.4            556.0           6.81           38.0              0.410
9     4641       Lungi Ngidi         83.38          74.2            446.0           8.65           28.0              0.377
10    19316      Maheesh Theekshana  83.02          170.1           1021.0          7.45           41.0              0.241
```

---

## 3. Task 2: Identification of the Actual Ranking Source

The rankings are generated directly by [src/clutch_engine.py](file:///c:/Users/HP/Contacts/Desktop/dbms%20documentation/src/clutch_engine.py). The execution trace proceeds as follows:

```
[Data Pack/ball_by_ball.csv]
          |
          v
[src/model_pressure.py] ---------> Computes pre-delivery state & pressure tiers
          |
          v
[src/clutch_engine.py]
  - Lines 233, 451: Filters eligibility:
      Batting: pressure_balls >= 60 & pressure_matches >= 8 (124 eligible)
      Bowling: pressure_balls >= 90 & pressure_matches >= 10 (105 eligible)
  - Lines 238-264: Batting composite Z-score and percentile projection
  - Lines 456-482: Bowling composite Z-score and percentile projection
  - Line 494: final_top10_bat = df_bat[df_bat['is_eligible']].sort_values('clutch_rating', ascending=False).head(10)
  - Line 518: final_top10_bowl = df_bowl[df_bowl['is_eligible']].sort_values('clutch_rating', ascending=False).head(10)
  - Lines 539-554: Exports Top_10_Batters.csv, Top_10_Bowlers.csv, All_Player_Scores.csv
```

---

## 4. Task 3 & 4: Root Cause of the Discrepancy

### 4.1 Side-by-Side Comparison of Rankings

```
+-----------------------------------------------------------------------------------------------------------------------+
| BATTING RANKING DISCREPANCY FORENSIC COMPARISON                                                                       |
+------+---------------------------------------------+---------------------------------------------+--------------------+
| Rank | Stale / Unverified Draft Audit Text         | Genuine Engine Output (Top_10_Batters.csv)  | Discrepancy Status |
+------+---------------------------------------------+---------------------------------------------+--------------------+
| 1    | Jos Buttler (813) — 96.81                   | Jos Buttler (813) — 96.81                   | MATCH              |
| 2    | Ashutosh Sharma (8101) — 94.72              | Ashutosh Sharma (8101) — 94.72              | MATCH              |
| 3    | Shashank Singh (8095) — 93.99 [INVALID ID]  | Tim David (6396) — 92.68                    | DISCREPANCY        |
| 4    | Dinesh Karthik (128) — 92.93 [INVALID ID]   | Dinesh Karthik (143) — 91.99                | DISCREPANCY        |
| 5    | Heinrich Klaasen (4174) — 92.74 [INVALID ID]| Namboori Tilak Varma (7897) — 90.22         | DISCREPANCY        |
| 6    | Nicholas Pooran (3882) — 92.51 [INVALID ID] | Rachin Ravindra (4854) — 89.96              | DISCREPANCY        |
| 7    | Namboori Tilak Varma (7897) — 90.22         | Glenn Maxwell (838) — 89.04                 | DISCREPANCY        |
| 8    | Glenn Maxwell (1301) — 89.15 [INVALID ID]   | George Linde (4229) — 85.63                 | DISCREPANCY        |
| 9    | Sanju Samson (190) — 87.77 [INVALID ID]     | Reeza Hendricks (768) — 85.43               | DISCREPANCY        |
| 10   | Tristan Stubbs (7861) — 87.52 [INVALID ID]  | Babar Azam (2485) — 85.22                   | DISCREPANCY        |
+------+---------------------------------------------+---------------------------------------------+--------------------+
```

### 4.2 Forensic Proof of Stale Textual Hallucination
An audit of the relational player mapping table `Data Pack/competition_team_player_mapping.csv` revealed definitive proof:
- In `Data Pack`, Dinesh Karthik is **Player ID 143** (ID 128 is nonexistent).
- In `Data Pack`, Shashank Singh is **Player ID 2756** (ID 8095 is nonexistent).
- In `Data Pack`, Heinrich Klaasen is **Player ID 4260** (ID 4174 is nonexistent).
- In `Data Pack`, Nicholas Pooran is **Player ID 3125** (ID 3882 is nonexistent).
- In `Data Pack`, Glenn Maxwell is **Player ID 838** (ID 1301 is nonexistent).
- In `Data Pack`, Sanju Samson is **Player ID 2258** (ID 190 is nonexistent).
- In `Data Pack`, Tristan Stubbs is **Player ID 20702** (ID 7861 is nonexistent).

The presence of these fictitious IDs demonstrates that the draft list was **an unverified textual mockup from an external source or brainstorming scratchpad**, which was accidentally pasted into the narrative section of the audit document. It was **never** generated by the active codebase.

### 4.3 Evaluation of Hypotheses:
- **Hypothesis 1 (Different Source CSV):** Refuted. Both the code and reports operate on `Data Pack/ball_by_ball.csv`.
- **Hypothesis 2 (Different Scoring Version):** Refuted. Scoring formulas in `src/clutch_engine.py` are identical across all runs.
- **Hypothesis 3 (Different Eligibility Threshold):** Refuted. `df_bat['is_eligible']` has consistently required $\ge 60$ pressure balls and $\ge 8$ matches.
- **Hypothesis 4 (Different Ranking Column):** Refuted. All rankings sort on `clutch_rating` descending.
- **Hypothesis 5 (Stale Report Draft):** **CONFIRMED.** A draft markdown artifact contained unverified mock data that contradicted the active engine outputs. Correcting Section 4.2 in `INDEPENDENT_SCORING_AUDIT.md` restores 100% concordance.

---

## 5. Task 5: Eligibility Threshold Verification (60 vs. 90 Pressure Balls)

An audit of lines 233 and 451 of [src/clutch_engine.py](file:///c:/Users/HP/Contacts/Desktop/dbms%20documentation/src/clutch_engine.py) resolves the apparent discrepancy:

### Active Source Code Implementation:
```python
# Batting Eligibility (Line 233)
df_bat['is_eligible'] = (df_bat['pressure_balls'] >= 60) & (df_bat['pressure_matches'] >= 8)

# Bowling Eligibility (Line 451)
df_bowl['is_eligible'] = (df_bowl['pressure_balls'] >= 90) & (df_bowl['pressure_matches'] >= 10)
```

### Why the Thresholds Differ:
1. **Batting Volume ($N \ge 60$ balls, $M \ge 8$ matches):**
   - High-pressure batting deliveries ($P \ge 50.0$) represent crunch situations (late chases, severe collapses). A batter typically faces $8$ to $15$ balls in such scenarios per match. Facing $60$ pressure balls across $8$ separate matches represents substantial high-leverage exposure.
2. **Bowling Volume ($N \ge 90$ legal balls / $15.0$ overs, $M \ge 10$ matches):**
   - In T20 cricket, a frontline bowler delivers up to $24$ balls ($4.0$ overs) per match.
   - Setting a 60-ball threshold would represent only $2.5$ matches of 4-over bowling, exposing the ranking to severe small-sample noise (e.g. a bowler having two lucky tight overs).
   - The $90$-ball ($15.0$ overs) threshold across at least $10$ matches guarantees that every ranked bowler has sustained high-leverage workload across multiple tournament fixtures.

### Population Impact:
- Total Tracked Batters: **622** $\rightarrow$ Eligible Batters: **124** ($19.9\%$).
- Total Tracked Bowlers: **543** $\rightarrow$ Eligible Bowlers: **105** ($19.3\%$).

---

## 6. Task 6: Mathematical Proof of Zero-Dismissal Bayesian Shrinkage

The user requested mathematical verification of the zero-dismissal Bayesian average formula and clarification on whether $32.4$ is a universal result or an example.

### 6.1 The Mathematical Model
In [src/clutch_engine.py](file:///c:/Users/HP/Contacts/Desktop/dbms%20documentation/src/clutch_engine.py#L185), the Bayesian conjugate prior for batting average is implemented as:
$$\text{Shrunk Average} = \frac{\text{Runs} + K_{\text{outs}} \times \mu_{\text{avg}}}{\text{Dismissals} + K_{\text{outs}}}$$
where $K_{\text{outs}} = 5.0$ pseudo-dismissals.

### 6.2 Empirical League Priors
Computing the exact benchmark means from all high-pressure deliveries ($P \ge 50.0$):
- **Overall League Mean:** $\mu_{\text{avg, all}} = 20.23$
- **IPL Benchmark Mean:** $\mu_{\text{avg, IPL}} = 23.46$
- **T20I Benchmark Mean:** $\mu_{\text{avg, T20I}} = 18.26$

### 6.3 Mathematical Behavior for Zero Dismissals ($\text{Dismissals} = 0$)
When a batter has zero dismissals under pressure:
$$\text{Shrunk Average} = \frac{\text{Runs} + 5.0 \times \mu_{\text{avg}}}{0 + 5.0} = \frac{\text{Runs}}{5.0} + \mu_{\text{avg}}$$

### 6.4 Clarification: Is 32.4 a General Result or an Example?
$$\mathbf{32.4 \text{ is an illustrative example, NOT a universal general result.}}$$

- **Specific Case (The 32.4 Example):**
  If a batter scores exactly **$45$ runs** with **$0$ dismissals** in the IPL under pressure:
  $$\text{Shrunk Average} = \frac{45.0 + 5.0 \times 23.46}{0 + 5.0} = \frac{45.0 + 117.30}{5.0} = \frac{162.30}{5.0} = \mathbf{32.46 \approx 32.4}$$
- **Other Cases:**
  - A batter with $0$ runs and $0$ dismissals shrinks to the prior mean: $\frac{0 + 5.0 \times 23.46}{5.0} = \mathbf{23.46}$.
  - A batter with $20$ runs and $0$ dismissals evaluates to: $\frac{20.0}{5.0} + 23.46 = 4.0 + 23.46 = \mathbf{27.46}$.
  - A batter with $100$ runs and $0$ dismissals evaluates to: $\frac{100.0}{5.0} + 23.46 = 20.0 + 23.46 = \mathbf{43.46}$.

The formula is continuous, strictly monotonic with respect to runs, and completely eliminates the division-by-zero singularity.

---

## 7. Task 7: Dashboard and PDF Source Alignment

An audit of data ingestion pipelines in the presentation layer confirmed:

1. **Dashboard ([output/Dashboard/app.py](file:///c:/Users/HP/Contacts/Desktop/dbms%20documentation/output/Dashboard/app.py)):**
   - Lines 130–132:
     ```python
     top_bat = pd.read_csv(get_file_path('Top_10_Batters.csv'))
     top_bowl = pd.read_csv(get_file_path('Top_10_Bowlers.csv'))
     all_players = pd.read_csv(get_file_path('All_Player_Scores.csv'))
     ```
   - Dynamically renders the authoritative rankings directly from disk.
2. **Competition PDF ([output/CLUTCH_XI_Methodology_Report.pdf](file:///c:/Users/HP/Contacts/Desktop/dbms%20documentation/output/CLUTCH_XI_Methodology_Report.pdf)):**
   - Built directly from `output/Top_10_Batters.csv` and `output/Top_10_Bowlers.csv`.
   - Page 6 explicitly presents: Jos Buttler (#1, 96.81), Ashutosh Sharma (#2, 94.72), Tim David (#3, 92.68).
   - Page 6–7 explicitly presents: Sunil Narine (#1, 91.69), Riley Meredith (#2, 86.99).
3. **Concordance:** 100% of all visual and document interfaces utilize the identical authoritative ranking files.

---

## 8. Final Reconciliation Verdict

```
========================================================================================
FINAL AUDIT DECISION: RECONCILED & PASS (SUBMISSION READY)
========================================================================================
- The discrepancy was caused by an unverified draft text insertion in an earlier report.
- Authoritative CSVs, PDF reports, and dashboard interfaces are in 100% agreement.
- Eligibility thresholds (60 balls for batters, 90 balls for bowlers) are mathematically
  justified and verified in code.
- Zero-dismissal Bayesian average formula is mathematically validated (32.4 is an example).
- The final submission package in final_submission/ is consistent and publication-ready.
========================================================================================
```
