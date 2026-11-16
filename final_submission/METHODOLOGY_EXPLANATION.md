# CLUTCH XI: Mathematical Methodology & Scoring Architecture

**Project:** CLUTCH XI — Rajasthan Royals SupeRR Selector Season 2  
**Document Type:** Formal Methodology Specification  
**Status:** Audited & Verified  

---

## 1. Problem Formulation: Beyond Volume-Based Cricket Analytics

Traditional cricket metrics suffer from fundamental context insensitivity:
1. **Linear Aggregation Fallacy:** A boundary hit in the 3rd over of a dead rubber counts identically to a boundary required off the final ball of a knockout chase.
2. **Small-Sample Distortion:** Batters dismissed 0 times in brief pressure appearances produce an infinite batting average ($\infty$), distorting standard ranking models.
3. **Format Asymmetry:** T20 International cricket features wider disparity in bowling attacks and pitch conditions, whereas the Indian Premier League (IPL) represents a concentrated, high-quality professional benchmark.
4. **Denominator Errors:** Dividing runs conceded by rounded decimal overs (e.g. $3.2$ overs $= 3.2$) instead of true legal overs ($3 + 2/6 = 3.333$) introduces systematic error in bowling economy rates.

**CLUTCH XI** resolves these issues through a contextual pressure index, empirical Bayes shrinkage, and a confidence-weighted format integration engine.

> **CRITICAL METHODOLOGICAL SCOPE:**  
> The CLUTCH XI pressure engine is a **situational stress and player resilience evaluation framework**. It measures how individual skill execution changes under heightened match demands. **It does NOT predict match-winning probability, and does NOT claim to estimate true game-theoretic win expectancy.**

---

## 2. Dynamic Ball-by-Ball Pressure Engine

Situational pressure ($P \in [0.0, 100.0]$) is evaluated on a continuous scale for every delivery using **pre-delivery state variables** (before the ball is bowled). This prevents data leakage.

### 2.1 Innings 1: Target Setting Pressure

In the first innings, pressure stems from score accumulation relative to expected par, wicket conservation, and match phase progression.

$$\text{Phase} = \frac{\text{legal\_balls\_before}}{\max(1, \text{sched\_balls})}$$
$$\text{Death Factor} = \text{clip}\left(\frac{\text{legal\_balls\_before} - 0.75 \times \text{sched\_balls}}{\max(1, 0.25 \times \text{sched\_balls})}, 0.0, 1.0\right)$$
$$\text{Expected Wickets} = 6.61 \times \text{Phase}$$
$$\text{Wicket Crisis} = \text{clip}\left(\frac{\text{actual\_wickets} - \text{Expected Wickets}}{3.0}, -0.5, 1.0\right)$$
$$\text{CRR Deficit} = \text{clip}\left(\frac{8.92 - \text{CRR}}{3.5}, -0.5, 1.0\right)$$
$$\text{Explosive Batting} = \text{clip}\left(\frac{\text{CRR} - 8.92}{3.5}, 0.0, 1.0\right)$$

#### Innings 1 Pressure Formulas:
$$\mathbf{P}_{\text{bat, inn1}} = 20.0 + 30.0 \times \max(0, \text{Wicket Crisis}) + 25.0 \times \max(0, \text{CRR Deficit}) + 25.0 \times \text{Death Factor}$$
$$\mathbf{P}_{\text{bowl, inn1}} = 20.0 + 35.0 \times \text{Death Factor} + 25.0 \times \text{Explosive Batting} + 20.0 \times \left(\frac{\text{wickets\_remaining}}{10}\right) \times (1.0 - \text{Death Factor})$$

- **Baseline:** Exactly $20.0$ on Ball 1 of Innings 1 (Low Pressure Tier).
- **Scheduled Balls:** Dynamically scaled to actual scheduled innings length ($30, 60, 72, 90,$ or $120$ balls) to handle shortened matches correctly.

---

### 2.2 Innings 2: Chasing Pressure

In the second innings, pressure is determined by chase urgency, required run rate (RRR), wicket scarcity, and match balance.

$$\text{RRR Factor} = \text{clip}\left(\frac{\text{RRR} - 6.0}{8.0}, 0.0, 1.0\right)$$
$$\text{Wicket Scarcity} = \text{clip}\left(\frac{10.0 - \text{wickets\_remaining}}{8.0}, 0.0, 1.0\right)$$

#### Chase Balance Proxy (Heuristic):
$$z = 1.25 \times \left(\frac{\text{wickets\_remaining}}{10.0}\right) - 0.25 \times (\text{RRR} - 8.92) - 0.35 \times (\text{Phase} - 0.5) - 1.0$$
$$\text{Chase Balance Proxy} = \frac{1}{1 + e^{-\text{clip}(z, -6.0, 6.0)}}$$
$$\text{Leverage} = 4.0 \times \text{Chase Balance Proxy} \times (1.0 - \text{Chase Balance Proxy})$$
$$\text{Defense Tension} = \text{clip}\left(\frac{\text{RRR} - 5.0}{7.0}, 0.0, 1.0\right) \times \left(\frac{\text{wickets\_remaining}}{10.0}\right)$$

#### Innings 2 Pressure Formulas:
$$\mathbf{P}_{\text{bat, inn2}} = \left(0.35 \times \text{RRR Factor} + 0.30 \times \text{Wicket Scarcity} + 0.20 \times \text{Phase} + 0.15 \times \text{Leverage}\right) \times 100.0$$
$$\mathbf{P}_{\text{bowl, inn2}} = \left(0.35 \times \text{Leverage} + 0.30 \times \text{Phase} + 0.20 \times \text{Defense Tension} + 0.15 \times (1.0 - \text{Wicket Scarcity})\right) \times 100.0$$

#### Situational Dampeners:
1. **Garbage-Time Blowouts (Chase Lost):** If Chase Balance Proxy $< 0.03$ in the final $25\%$ of balls remaining:
   $$\mathbf{P}_{\text{bat}} = \max(20.0, \mathbf{P}_{\text{bat}} \times 0.5), \quad \mathbf{P}_{\text{bowl}} = \max(15.0, \mathbf{P}_{\text{bowl}} \times 0.4)$$
2. **Effectively Won Chases:** If Chase Balance Proxy $> 0.97$ and $\le 10$ runs needed with reliable target:
   $$\mathbf{P}_{\text{bat}} = \min(25.0, \mathbf{P}_{\text{bat}} \times 0.4), \quad \mathbf{P}_{\text{bowl}} = \max(15.0, \mathbf{P}_{\text{bowl}} \times 0.4)$$
3. **Post-Win Deliveries:** If $\text{runs\_before} \ge \text{target}$ on a reliable target, $\mathbf{P} = 15.0$.

---

### 2.3 Super Overs (Innings 3 & 4)

Super Overs represent the absolute pinnacle of high-leverage cricket:
$$\mathbf{P}_{\text{bat, Super Over}} = 100.0, \quad \mathbf{P}_{\text{bowl, Super Over}} = 100.0$$
Super Overs are identified through dual criteria: innings index $\ge 3$ AND match result containing tied/super over text.

---

### 2.4 Pressure Tiers

Every delivery is categorized into one of four operational pressure tiers:
- **Low Pressure ($P < 30.0$):** Standard cruise-control situations, early powerplay overs with full wickets.
- **Medium Pressure ($30.0 \le P < 50.0$):** Competitive game progression, balanced run rates.
- **High Pressure ($50.0 \le P < 75.0$):** Crunch inflection points, accelerating run rates, declining wickets.
- **Extreme Pressure ($P \ge 75.0$):** Severe crisis overs, death chases with high RRR, Super Overs.

---

## 3. Performance Metrics Under Pressure

For players active in High Pressure situations ($P \ge 50.0$):

### 3.1 Cricket Law Compliance
- **Batter Balls Faced:** Computed as deliveries where `extras_type != 'wide'`. Includes no-balls.
- **Bowler Legal Balls Bowled:** Computed as deliveries where `extras_type not in ['wide', 'Overstep', 'other']`.
- **Bowler Runs Conceded:**
  $$\text{Runs Conceded} = \text{batter\_runs} + \text{wides} + \text{no\_balls}$$
  Fielding extras (byes and leg-byes) are strictly excluded from the bowler's figures.
- **Bowler Wickets:** Strictly bowler-credited dismissals (`bowled`, `caught`, `lbw`, `stumped`, `hit wicket`). Runouts and obstructing the field are excluded.
- **True Bowling Rate Calculations:**
  $$\text{True Economy} = \frac{\text{bowler\_runs\_conceded} \times 6.0}{\text{legal\_balls\_bowled}}$$
  $$\text{Wickets Per Over (WPO)} = \frac{\text{bowler\_wickets} \times 6.0}{\text{legal\_balls\_bowled}}$$

---

## 4. Bayesian Shrinkage & Conjugate Priors

To prevent small-sample volatility and resolve the zero-dismissal division problem:

### 4.1 Batting Strike Rate Shrinkage
$$\text{Shrunk SR} = \frac{N_{\text{balls}}}{N_{\text{balls}} + K_{\text{sr}}} \times \text{Raw SR} + \frac{K_{\text{sr}}}{N_{\text{balls}} + K_{\text{sr}}} \times \mu_{\text{sr}}, \quad K_{\text{sr}} = 30.0 \text{ balls}$$

### 4.2 Batting Average Shrinkage (Conjugate Prior)
For batters who are rarely dismissed under pressure:
$$\text{Shrunk Avg} = \frac{\text{Runs} + K_{\text{outs}} \times \mu_{\text{avg}}}{\text{Dismissals} + K_{\text{outs}}}, \quad K_{\text{outs}} = 5.0 \text{ outs}$$
When $\text{Dismissals} = 0$, the formula gracefully evaluates to $\frac{\text{Runs} + 5.0 \times \mu_{\text{avg}}}{5.0}$, preventing infinite averages while crediting runs scored.

### 4.3 Bowling Rate Shrinkage
$$\text{Shrunk Econ} = \frac{N_{\text{balls}}}{N_{\text{balls}} + K_{\text{bowl}}} \times \text{Raw Econ} + \frac{K_{\text{bowl}}}{N_{\text{balls}} + K_{\text{bowl}}} \times \mu_{\text{econ}}, \quad K_{\text{bowl}} = 36.0 \text{ legal balls}$$
$$\text{Shrunk WPO} = \frac{N_{\text{balls}}}{N_{\text{balls}} + K_{\text{bowl}}} \times \text{Raw WPO} + \frac{K_{\text{bowl}}}{N_{\text{balls}} + K_{\text{bowl}}} \times \mu_{\text{wpo}}, \quad K_{\text{bowl}} = 36.0 \text{ legal balls}$$

---

## 5. Confidence-Weighted 70/30 Format Blending

The model blends IPL and T20I data using a confidence-weighted mechanism that reflects format depth and competitive quality.

### 5.1 Format Sample Confidence
$$C_{\text{IPL}} = 1.0 - e^{-N_{\text{IPL}} / 40.0}, \quad C_{\text{T20I}} = 1.0 - e^{-N_{\text{T20I}} / 40.0}$$

### 5.2 Dynamic Weight Allocation
$$\text{Denom} = 0.70 \times C_{\text{IPL}} + 0.30 \times C_{\text{T20I}}$$
$$w_{\text{IPL}} = \begin{cases} \frac{0.70 \times C_{\text{IPL}}}{\text{Denom}} & \text{if } C_{\text{IPL}} > 0 \text{ and } C_{\text{T20I}} > 0 \\ 1.0 & \text{if } C_{\text{IPL}} > 0 \text{ and } C_{\text{T20I}} = 0 \\ 0.0 & \text{if } C_{\text{IPL}} = 0 \end{cases}$$
$$w_{\text{T20I}} = 1.0 - w_{\text{IPL}}$$

### 5.3 Environmental Normalization
T20I statistics are mapped to the IPL par benchmark:
$$\text{T20I}_{\text{SR, adj}} = \mu_{\text{SR, IPL}} + (\text{SR}_{\text{T20I, shrunk}} - \mu_{\text{SR, T20I}})$$
$$\text{T20I}_{\text{Econ, adj}} = \mu_{\text{Econ, IPL}} + (\text{Econ}_{\text{T20I, shrunk}} - \mu_{\text{Econ, T20I}})$$

### 5.4 Format Calibration Factor
To account for the superior competitive density and tactical scouting of the IPL:
$$\text{Format Factor} = \begin{cases} 1.00 & \text{if player has IPL evidence } (C_{\text{IPL}} > 0) \\ 0.90 & \text{if player has pure T20I evidence } (C_{\text{IPL}} = 0) \end{cases}$$

---

## 6. Composite Scoring & Final Clutch Rating

### 6.1 Batting Composite Score ($Z_{\text{bat}}$)
Standardized across the eligible batting population ($\ge 60$ pressure balls, $\ge 8$ matches):
$$Z_{\text{bat}} = 0.20 Z_{\text{SR}} + 0.05 Z_{\text{Avg}} + 0.20 Z_{\Delta\text{SR}} + 0.15 Z_{\text{Bdry}-\text{Dot}} + 0.15 Z_{\text{Extreme}} + 0.15 Z_{\text{Consist}} + 0.10 Z_{\text{Comp}}$$

### 6.2 Bowling Composite Score ($Z_{\text{bowl}}$)
Standardized across the eligible bowling population ($\ge 90$ legal pressure balls, $\ge 10$ matches):
$$Z_{\text{bowl}} = 0.20 Z_{\text{Econ}} + 0.20 Z_{\text{WPO}} + 0.15 Z_{\Delta\text{Econ}} + 0.15 Z_{\text{Dot}-\text{Bdry}} + 0.10 Z_{\text{Extreme}} + 0.10 Z_{\text{Consist}} + 0.10 Z_{\text{Comp}}$$

### 6.3 Final Clutch Rating
The composite $Z$-score is mapped to a percentile rating via the standard normal cumulative distribution function $\Phi$, scaled by sample confidence and format factor:
$$\text{Raw Percentile} = \Phi(Z_{\text{composite}}) \times 100.0$$
$$\text{Overall Confidence} = 1.0 - e^{-N_{\text{pressure\_balls}} / 50.0}$$
$$\mathbf{\text{Clutch Rating}} = \text{clip}\left(\text{Raw Percentile} \times (0.80 + 0.20 \times \text{Overall Confidence}) \times \text{Format Factor}, 0.0, 99.5\right)$$

---

## 7. How to Interpret the Final Ratings

- **90.0 – 99.5 (Elite Clutch Match-Winner):** World-class crisis performers who consistently elevate their baseline scoring or containment when match demands spike. (e.g. Jos Buttler 96.81, Sunil Narine 91.69).
- **80.0 – 89.9 (High-Leverage Core Specialist):** Proven performers with positive expectation-adjusted deltas and strong boundary/dot ratios. (e.g. Tim David 92.68, Riley Meredith 86.99).
- **70.0 – 79.9 (Reliable Role Player):** Capable contributors who maintain neutral performance under pressure.
- **Below 60.0 (Pressure Vulnerable):** Players whose strike rates decline significantly or whose economy rates leak excessively in high-stress overs.
