# CLUTCH XI: Pressure Intelligence & Player Reliability Analytics
## Rajasthan Royals — SupeRR Selector Season 2 | Round 1 Submission

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg)](https://streamlit.io)
[![Status](https://img.shields.io/badge/Audit-Deterministic%20Pass-brightgreen.svg)]()

> **"Beyond Statistics. Identifying Players Who Deliver Under Pressure."**

---

## 📌 Executive Summary

Championships in the Indian Premier League are decided at high-stress inflection points: closing out steep chases requiring 12+ an over, defending compressed margins in the death overs, or arresting a top-order collapse at 35/3. Traditional volume metrics—aggregate runs, career strike rates, and raw economy—fail to differentiate between low-leverage cruise control and high-pressure clutch execution.

**CLUTCH XI** is an enterprise-grade quantitative intelligence system engineered from the proprietary **Rajasthan Royals Data Pack** (200,999 deliveries across 883 matches from 2022 to 2026). It evaluates every delivery through a continuous situational pressure index (0 to 100), combining required run rates, resource depletion, match phase urgency, and leverage strictly prior to the delivery outcome.

---

## 🏆 Authoritative Top 10 Rankings

### Top 10 Batters Under Pressure
| Rank | Player Name | Player ID | Clutch Rating | Pressure SR | Extreme SR | Pressure Avg | Pressure Balls | Tactical Role |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **#1** | **Jos Buttler** | 813 | **96.81** | 181.4 | 237.9 | 45.7 | 252 | Designated Chase Master / Opener |
| **#2** | **Ashutosh Sharma** | 8101 | **94.72** | 177.3 | 192.2 | 28.1 | 238 | Lower-Order Power Finisher (#7/#8) |
| **#3** | **Tim David** | 6396 | **92.68** | 186.6 | 195.4 | 33.3 | 446 | Primary Death-Overs Closer (#6) |
| **#4** | **Dinesh Karthik** | 143 | **91.99** | 186.1 | 168.3 | 38.9 | 209 | Veteran Finishing Specialist / WK |
| **#5** | **Namboori Tilak Varma** | 7897 | **90.22** | 155.3 | 188.9 | 56.6 | 729 | Middle-Order Crisis Stabilizer (#4) |
| **#6** | **Rachin Ravindra** | 4854 | **89.96** | 172.9 | 143.5 | 29.1 | 118 | Dynamic Top-Order Floater (#3) |
| **#7** | **Glenn Maxwell** | 838 | **89.04** | 175.9 | 223.5 | 33.2 | 245 | Middle-Overs Counter-Attacker |
| **#8** | **George Linde** | 4229 | **85.63** | 173.5 | 195.5 | 18.0 | 83 | Lower-Order Hitting All-Rounder |
| **#9** | **Reeza Hendricks** | 768 | **85.43** | 167.0 | 142.9 | 77.2 | 185 | High-Floor Anchor (T20I Spec) |
| **#10** | **Babar Azam** | 2485 | **85.22** | 183.5 | 218.2 | 52.0 | 85 | Top-Order Anchor / Stabilizer |

### Top 10 Bowlers Under Pressure
| Rank | Player Name | Player ID | Clutch Rating | Pressure Econ | Extreme Econ | Pressure WPO | Pressure Overs | Tactical Role |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **#1** | **Sunil Narine** | 781 | **91.69** | 6.95 | 7.43 | 0.269 | 126.3 | High-Leverage Choke Spinner / PP |
| **#2** | **Riley Meredith** | 5940 | **86.99** | 8.45 | 7.33 | 0.436 | 18.2 | Middle/Death Strike Pace Weapon |
| **#3** | **Liam Dawson** | 722 | **86.40** | 5.77 | 7.33 | 0.412 | 21.5 | PP & Middle Containment Spinner |
| **#4** | **Mitchell Santner** | 4101 | **85.91** | 7.32 | 6.97 | 0.344 | 159.5 | High-Control Finger Spinner / #8 |
| **#5** | **Sufiyan Muqeem** | 34485 | **84.77** | 5.07 | 5.60 | 0.401 | 47.2 | Mystery Wrist Spinner / Wicket-Taker |
| **#6** | **Mark Wood** | 2985 | **84.61** | 8.70 | 6.60 | 0.626 | 30.2 | Express Pace Enforcer (9.6 b/wkt) |
| **#7** | **Rashid Khan** | 4722 | **84.09** | 7.45 | 7.56 | 0.350 | 222.4 | Primary Strike Leg-Spinner |
| **#8** | **Mohammad Nawaz** | 2490 | **83.50** | 6.81 | 7.50 | 0.410 | 92.4 | Matchup Left-Arm Finger Spinner |
| **#9** | **Lungi Ngidi** | 4641 | **83.38** | 8.65 | 5.00 | 0.377 | 74.2 | Hit-the-Deck Death Overs Seamer |
| **#10** | **Maheesh Theekshana** | 19316 | **83.02** | 7.45 | 7.50 | 0.241 | 170.1 | Powerplay & Death Carrom Specialist |

---

## 🚀 How to Launch the Interactive Streamlit Dashboard

The repository includes a full-featured, dark-themed interactive Rajasthan Royals analytics dashboard:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch the Streamlit application
streamlit run output/Dashboard/app.py
```

### Dashboard Features:
1. **Executive Overview:** High-level KPI metrics and pre-delivery pressure distribution histograms.
2. **Pressure Intelligence:** Interactive mathematical formulation explorer and situational pie charts.
3. **Top 10 Batters & Bowlers:** Dynamic ranking tables, interactive Plotly comparison charts, and individual player focus cards.
4. **Player Explorer:** Live search across all 1,217 players tracked in the Rajasthan Royals data pack.
5. **RR Auction Intelligence:** Tactical player acquisition tiers and auction decision matrix.
6. **Methodology & Sensitivity:** Complete audit reports, robustness testing, and unit test logs.

---

## 📂 Repository Structure

```
clutch-xi-rajasthan-royals/
├── final_submission/
│   ├── CLUTCH_XI_Rajasthan_Royals_Round1_Submission.pdf  # Authoritative 12-Page Submission Report
│   ├── Top_10_Batters.csv                                # Official Dropdown-Matched Rankings
│   ├── Top_10_Bowlers.csv                                # Official Dropdown-Matched Rankings
│   ├── All_Player_Scores.csv                             # Full 958-Player Scored Cohort
│   ├── Data_Quality_Report.csv                           # Relational Validation & Quality Log
│   ├── Sensitivity_Analysis.csv                          # Threshold & Weight Robustness Matrix
│   └── figures/                                          # Vector Publication Visualizations
├── output/
│   ├── Dashboard/
│   │   └── app.py                                        # Interactive Streamlit Web Application
│   ├── Top_10_Batters.csv
│   └── Top_10_Bowlers.csv
├── src/
│   ├── model_pressure.py                                 # Pre-Delivery Pressure State Vector Engine
│   └── clutch_engine.py                                  # Standardized Scoring & Bayesian Normalization
├── scripts/
│   └── build_competition_pdf.py                          # Automated ReportLab 12-Page PDF Generator
├── requirements.txt
└── README.md
```

---

## 🔬 Mathematical Architecture Highlights

- **Zero Data Leakage:** Every situational variable is calculated strictly *prior* to delivery execution.
- **Asymmetric Match Tension:** Batting pressure balances required run rate against wicket scarcity; bowling pressure tracks match volatility and death proximity.
- **Conjugate Bayesian Shrinkage:** Mitigates small-sample anomalies by shrinking low-sample metrics towards league par (K_sr=30, K_outs=5, K_bowl=36).
- **Cross-Format Difficulty Normalization:** 70/30 IPL-to-T20I difficulty calibration prevents international inflation.

---

## 📄 Attribution & License
Prepared exclusively for the **Rajasthan Royals SupeRR Selector Season 2 (Round 1 Submission)**. Data foundation based on the official Rajasthan Royals Data Pack.
