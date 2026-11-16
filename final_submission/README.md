# CLUTCH XI: Official Submission Package
## Rajasthan Royals — SupeRR Selector Season 2 | Round 1

**Authors:** Senior Cricket Data Scientist & Quantitative Analytics Group  
**Target:** Competition Submission Package  
**Tagline:** *Beyond averages. Built for the moments that decide matches.*  

---

## 1. Submission Package Overview

This directory (`final_submission/`) contains the complete, submission-ready deliverable package for **CLUTCH XI**, verified against the audited Stage 3 scoring engine.

### Package File Inventory:
```
final_submission/
├── CLUTCH_XI_Methodology_Report.pdf   # Official 8-Page Competition Submission Document
├── PROJECT_REPORT.md                  # Comprehensive Markdown Project Report
├── Top_10_Batters.csv                 # Verified Top 10 Batters Under Pressure (10 rows)
├── Top_10_Bowlers.csv                 # Verified Top 10 Bowlers Under Pressure (10 rows)
├── All_Player_Scores.csv              # Complete 958-Player Pressure Dataset
├── Player_Performance_Summary.csv     # Ranked Performance Summary (Sorted by Clutch Rating)
├── Data_Quality_Report.csv            # Relational Schema & Quality Validation Summary
├── Sensitivity_Analysis.csv           # Robustness Testing Across Thresholds & Weights
├── METHODOLOGY_EXPLANATION.md         # Detailed Mathematical & Algorithmic Formulation
├── DATASET_DESCRIPTION.md             # Data Pack Schemas, Cricket Rules & Match 48610 Audit
├── TECHNICAL_ARCHITECTURE.md          # Pipeline Architecture & Data Flow Specification
├── LIMITATIONS_AND_FUTURE_WORK.md     # Transparent Limitation Accounting & Future Roadmap
├── README.md                          # This Execution & Submission Guide
└── figures/                           # High-Resolution Publication Charts (PNG)
    ├── chart1_pressure_distribution.png
    ├── chart2_batters_comparison.png
    ├── chart3_bowlers_scatter.png
    └── chart4_format_divergence.png
```

---

## 2. Official Top 10 Rankings

### Top 10 Batters Under Pressure:
1. **Jos Buttler** (Player ID: 813) — Clutch Rating: **96.81** (Pressure SR: 181.35, Extreme SR: 237.93)
2. **Ashutosh Sharma** (Player ID: 8101) — Clutch Rating: **94.72** (Pressure SR: 177.31, Extreme SR: 192.22)
3. **Tim David** (Player ID: 6396) — Clutch Rating: **92.68** (Pressure SR: 186.55, Extreme SR: 195.39)
4. **Dinesh Karthik** (Player ID: 143) — Clutch Rating: **91.99** (Pressure SR: 186.12, Extreme SR: 168.29)
5. **Namboori Tilak Varma** (Player ID: 7897) — Clutch Rating: **90.22** (Pressure SR: 155.28, Extreme SR: 188.89)
6. **Rachin Ravindra** (Player ID: 4854) — Clutch Rating: **89.96** (Pressure SR: 172.88, Extreme SR: 143.48)
7. **Glenn Maxwell** (Player ID: 838) — Clutch Rating: **89.04** (Pressure SR: 175.92, Extreme SR: 223.53)
8. **George Linde** (Player ID: 4229) — Clutch Rating: **85.63** (Pressure SR: 173.49, Extreme SR: 195.45)
9. **Reeza Hendricks** (Player ID: 768) — Clutch Rating: **85.43** (Pressure SR: 167.03, Extreme SR: 142.86)
10. **Babar Azam** (Player ID: 2485) — Clutch Rating: **85.22** (Pressure SR: 183.53, Extreme SR: 218.18)

### Top 10 Bowlers Under Pressure:
1. **Sunil Narine** (Player ID: 781) — Clutch Rating: **91.69** (Pressure Econ: 6.95, Extreme Econ: 7.43)
2. **Riley Meredith** (Player ID: 5940) — Clutch Rating: **86.99** (Pressure Econ: 8.45, Extreme Econ: 7.33)
3. **Liam Dawson** (Player ID: 722) — Clutch Rating: **86.40** (Pressure Econ: 5.77, Extreme Econ: 7.33)
4. **Mitchell Santner** (Player ID: 4101) — Clutch Rating: **85.91** (Pressure Econ: 7.32, Extreme Econ: 6.97)
5. **Sufiyan Muqeem** (Player ID: 34485) — Clutch Rating: **84.77** (Pressure Econ: 5.07, Extreme Econ: 5.60)
6. **Mark Wood** (Player ID: 2985) — Clutch Rating: **84.61** (Pressure Econ: 8.70, Extreme Econ: 6.60)
7. **Rashid Khan** (Player ID: 4722) — Clutch Rating: **84.09** (Pressure Econ: 7.45, Extreme Econ: 7.56)
8. **Mohammad Nawaz** (Player ID: 2490) — Clutch Rating: **83.50** (Pressure Econ: 6.81, Extreme Econ: 7.50)
9. **Lungi Ngidi** (Player ID: 4641) — Clutch Rating: **83.38** (Pressure Econ: 8.65, Extreme Econ: 5.00)
10. **Maheesh Theekshana** (Player ID: 19316) — Clutch Rating: **83.02** (Pressure Econ: 7.45, Extreme Econ: 7.50)

---

## 3. How to Launch the Interactive Analytics Dashboard

The interactive Streamlit dashboard is fully operational and provides visual exploration of all metrics, player comparisons, and auction recommendations:

```bash
streamlit run output/Dashboard/app.py
```

---

## 4. Execution & Automated Verification Instructions

To re-run the verification tests across the generated CSVs:

```bash
# Verify integrity of Top 10 rankings and zero NaNs
python -c "import pandas as pd; b = pd.read_csv('final_submission/Top_10_Batters.csv'); w = pd.read_csv('final_submission/Top_10_Bowlers.csv'); print('Batters:', len(b), 'Bowlers:', len(w), 'Clean:', not b['clutch_rating'].isna().any() and not w['clutch_rating'].isna().any())"
```
