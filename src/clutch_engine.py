"""
CLUTCH XI: Audited & Defensible Scoring and Ranking Engine
Rajasthan Royals — SupeRR Selector Season 2 | Round 1

Comprehensive Scoring & Ranking Architecture:
- Batting: Batter-specific runs exclusively (zero extras credited to batters).
- Bowling: Exact rate calculations (runs * 6 / legal_balls, wickets * 6 / legal_balls; zero decimal-overs division).
- Legal Cricket Notation: Overs displayed strictly as (balls // 6) + (balls % 6) / 10.0 (e.g. 47.2 overs).
- Batting Average Shrinkage: Empirical Bayes conjugate prior based on dismissals (K_outs = 5.0).
- Consistency Calculations: Sample-size adjusted consistency via Bayesian shrinkage of CV towards league priors.
- Format Blending: Confidence-weighted 70% IPL / 30% T20I framework with environment normalization.
- Bowling 7-Component Composite: Explicitly includes competition-relative component (z_comp, 10%), summing to 1.00.
- Statistical Safeguards: safe_zscore handling zero variance, strict NaN/Inf immunity, reproducible rankings.
"""

import os
import sys
import pandas as pd
import numpy as np
from scipy import stats

print("=" * 70)
print("CLUTCH XI: RUNNING AUDITED SCORING & RANKING ENGINE")
print("=" * 70)

# Import model_pressure module which computes delivery-level state & pressure
from model_pressure import bbb_df, matches_df

# Load metadata
comp_df = pd.read_csv('Data Pack/competitions.csv')
p11_df = pd.read_csv('Data Pack/playing_eleven.csv').drop_duplicates(subset=['match_id', 'player_id'], keep='first')
mapping_df = pd.read_csv('Data Pack/competition_team_player_mapping.csv')

print(f"Total analyzed deliveries: {len(bbb_df):,}")

# Statistical helper functions
def safe_zscore(series):
    """Computes standardized Z-score with full protection against zero standard deviation and NaNs."""
    arr = np.asarray(series, dtype=float)
    std = np.nanstd(arr)
    if std == 0 or np.isnan(std):
        return np.zeros_like(arr)
    mean = np.nanmean(arr)
    return np.nan_to_num((arr - mean) / std, nan=0.0)

def to_cricket_overs(legal_balls):
    """Converts legal delivery count to standard cricket overs notation (e.g. 11 balls -> 1.5 overs)."""
    balls = int(legal_balls)
    return (balls // 6) + (balls % 6) / 10.0

# Export complete delivery analysis dataset (full 200,999 deliveries, no arbitrary sampling)
print("Exporting Pressure_Delivery_Analysis.csv (full delivery dataset)...")
delivery_summary = bbb_df[['match_id', 'innings', 'overid', 'over_ball_num', 
                           'striker_id', 'striker_name', 'bowler_id', 'bowler_name',
                           'runs_before', 'wickets_before', 'runs_needed', 'rrr', 'crr',
                           'batting_pressure', 'bat_tier', 'bowling_pressure', 'bowl_tier',
                           'runs', 'bowler_runs_conceded', 'is_wicket', 'is_bowler_wicket', 
                           'is_target_reliable', 'is_ipl', 'match_format', 'season']]
delivery_summary.to_csv('output/Pressure_Delivery_Analysis.csv', index=False)
print(f"Pressure_Delivery_Analysis.csv saved with {len(delivery_summary):,} rows.")

# -------------------------------------------------------------------------
# BATTING ANALYTICS & CLUTCH RATING
# -------------------------------------------------------------------------
print("\nCalculating Comprehensive Batting Metrics...")

bbb_df['is_batter_ball'] = (bbb_df['extras_type'] != 'wide')
bbb_df['is_batter_out'] = (bbb_df['is_wicket'] == True) & (bbb_df['dismissed_player_id'] == bbb_df['striker_id'])
bbb_df['is_batter_dot'] = (bbb_df['runs'] == 0) & bbb_df['is_batter_ball']

# Pressure deliveries mask (Pressure >= 50)
p_mask_bat = bbb_df['batting_pressure'] >= 50
p_delivs_bat = bbb_df[p_mask_bat]

# Format subsets under pressure
ipl_p_bat = p_delivs_bat[p_delivs_bat['is_ipl']]
t20i_p_bat = p_delivs_bat[p_delivs_bat['match_format'] == 'T20I']

# Benchmark population means
mu_sr_all_bat = (p_delivs_bat['runs'].sum() / p_delivs_bat['is_batter_ball'].sum()) * 100.0
mu_avg_all_bat = p_delivs_bat['runs'].sum() / max(1, p_delivs_bat['is_batter_out'].sum())

mu_sr_ipl_bat = (ipl_p_bat['runs'].sum() / ipl_p_bat['is_batter_ball'].sum()) * 100.0
mu_avg_ipl_bat = ipl_p_bat['runs'].sum() / max(1, ipl_p_bat['is_batter_out'].sum())

mu_sr_t20i_bat = (t20i_p_bat['runs'].sum() / t20i_p_bat['is_batter_ball'].sum()) * 100.0
mu_avg_t20i_bat = t20i_p_bat['runs'].sum() / max(1, t20i_p_bat['is_batter_out'].sum())

# Overall aggregates across all deliveries
overall_inns_bat = bbb_df[['striker_id', 'match_id', 'innings']].drop_duplicates().groupby('striker_id').size().rename('overall_innings')
overall_bat = bbb_df.groupby(['striker_id', 'striker_name']).agg(
    overall_runs=('runs', 'sum'),
    overall_balls=('is_batter_ball', 'sum'),
    overall_outs=('is_batter_out', 'sum'),
    overall_fours=('is_four', 'sum'),
    overall_sixes=('is_six', 'sum'),
    overall_dots=('is_batter_dot', 'sum'),
    overall_matches=('match_id', 'nunique'),
).reset_index().merge(overall_inns_bat, on='striker_id', how='left')
overall_bat['overall_sr'] = np.where(overall_bat['overall_balls'] > 0, (overall_bat['overall_runs'] / overall_bat['overall_balls']) * 100.0, 0.0)
overall_bat['overall_avg'] = np.where(overall_bat['overall_outs'] > 0, overall_bat['overall_runs'] / overall_bat['overall_outs'], overall_bat['overall_runs'])

# Pressure aggregates (P >= 50)
p_inns_bat = p_delivs_bat[['striker_id', 'match_id', 'innings']].drop_duplicates().groupby('striker_id').size().rename('pressure_innings')
p_bat_grp = p_delivs_bat.groupby(['striker_id', 'striker_name']).agg(
    pressure_runs=('runs', 'sum'),
    pressure_balls=('is_batter_ball', 'sum'),
    pressure_outs=('is_batter_out', 'sum'),
    pressure_fours=('is_four', 'sum'),
    pressure_sixes=('is_six', 'sum'),
    pressure_dots=('is_batter_dot', 'sum'),
    pressure_matches=('match_id', 'nunique'),
).reset_index().merge(p_inns_bat, on='striker_id', how='left')
p_bat_grp['pressure_sr'] = np.where(p_bat_grp['pressure_balls'] > 0, (p_bat_grp['pressure_runs'] / p_bat_grp['pressure_balls']) * 100.0, 0.0)
p_bat_grp['pressure_avg'] = np.where(p_bat_grp['pressure_outs'] > 0, p_bat_grp['pressure_runs'] / p_bat_grp['pressure_outs'], p_bat_grp['pressure_runs'])
p_bat_grp['pressure_bdry_pct'] = np.where(p_bat_grp['pressure_balls'] > 0, ((p_bat_grp['pressure_fours'] + p_bat_grp['pressure_sixes']) / p_bat_grp['pressure_balls']) * 100.0, 0.0)
p_bat_grp['pressure_dot_pct'] = np.where(p_bat_grp['pressure_balls'] > 0, (p_bat_grp['pressure_dots'] / p_bat_grp['pressure_balls']) * 100.0, 0.0)

# High pressure (50 <= P < 70)
h_mask_bat = (bbb_df['batting_pressure'] >= 50) & (bbb_df['batting_pressure'] < 70)
h_bat_grp = bbb_df[h_mask_bat].groupby(['striker_id', 'striker_name']).agg(
    high_runs=('runs', 'sum'), high_balls=('is_batter_ball', 'sum'), high_outs=('is_batter_out', 'sum')
).reset_index()
h_bat_grp['high_sr'] = np.where(h_bat_grp['high_balls'] > 0, (h_bat_grp['high_runs'] / h_bat_grp['high_balls']) * 100.0, 0.0)

# Extreme pressure (P >= 70)
e_mask_bat = bbb_df['batting_pressure'] >= 70
e_bat_grp = bbb_df[e_mask_bat].groupby(['striker_id', 'striker_name']).agg(
    extreme_runs=('runs', 'sum'), extreme_balls=('is_batter_ball', 'sum'), extreme_outs=('is_batter_out', 'sum'),
    extreme_fours=('is_four', 'sum'), extreme_sixes=('is_six', 'sum')
).reset_index()
e_bat_grp['extreme_sr'] = np.where(e_bat_grp['extreme_balls'] > 0, (e_bat_grp['extreme_runs'] / e_bat_grp['extreme_balls']) * 100.0, 0.0)

# Normal pressure (P < 50)
n_mask_bat = bbb_df['batting_pressure'] < 50
n_bat_grp = bbb_df[n_mask_bat].groupby(['striker_id', 'striker_name']).agg(
    normal_runs=('runs', 'sum'), normal_balls=('is_batter_ball', 'sum'), normal_outs=('is_batter_out', 'sum')
).reset_index()
n_bat_grp['normal_sr'] = np.where(n_bat_grp['normal_balls'] > 0, (n_bat_grp['normal_runs'] / n_bat_grp['normal_balls']) * 100.0, 0.0)

# Merge overall and tier subsets
df_bat = overall_bat.merge(p_bat_grp, on=['striker_id', 'striker_name'], how='left').fillna(0)
df_bat = df_bat.merge(h_bat_grp, on=['striker_id', 'striker_name'], how='left').fillna(0)
df_bat = df_bat.merge(e_bat_grp, on=['striker_id', 'striker_name'], how='left').fillna(0)
df_bat = df_bat.merge(n_bat_grp, on=['striker_id', 'striker_name'], how='left').fillna(0)

# Match consistency with Bayesian shrinkage of CV towards league mean (0.85)
m_runs_bat = p_delivs_bat.groupby(['striker_id', 'match_id'])['runs'].sum().reset_index()
m_agg_bat = m_runs_bat.groupby('striker_id')['runs'].agg(['std', 'mean', 'count']).reset_index()
m_agg_bat['raw_cv'] = np.where(m_agg_bat['mean'] > 0, m_agg_bat['std'].fillna(m_agg_bat['mean']) / m_agg_bat['mean'], 1.5)
Km = 5.0
m_agg_bat['shrunk_cv'] = (m_agg_bat['count'] / (m_agg_bat['count'] + Km)) * m_agg_bat['raw_cv'] + (Km / (m_agg_bat['count'] + Km)) * 0.85
m_agg_bat['match_consistency'] = np.clip(1.0 - (m_agg_bat['shrunk_cv'] / 2.0), 0.1, 1.0)
df_bat = df_bat.merge(m_agg_bat[['striker_id', 'match_consistency']], on='striker_id', how='left').fillna({'match_consistency': 0.3})

# Season consistency with Bayesian shrinkage
s_runs_bat = p_delivs_bat.groupby(['striker_id', 'season'])['runs'].sum().reset_index()
s_agg_bat = s_runs_bat.groupby('striker_id')['runs'].agg(['std', 'mean', 'count']).reset_index()
s_agg_bat['raw_cv'] = np.where(s_agg_bat['mean'] > 0, s_agg_bat['std'].fillna(s_agg_bat['mean']) / (s_agg_bat['mean'] + 1e-5), 1.5)
Ks = 2.0
s_agg_bat['shrunk_cv'] = (s_agg_bat['count'] / (s_agg_bat['count'] + Ks)) * s_agg_bat['raw_cv'] + (Ks / (s_agg_bat['count'] + Ks)) * 0.85
s_agg_bat['season_consistency'] = np.clip(1.0 - (s_agg_bat['shrunk_cv'] / 2.0), 0.1, 1.0)
df_bat = df_bat.merge(s_agg_bat[['striker_id', 'season_consistency']], on='striker_id', how='left').fillna({'season_consistency': 0.3})

# Format-specific aggregates
# 1. IPL under pressure
ipl_bat_grp = ipl_p_bat.groupby('striker_id').agg(
    ipl_p_runs=('runs', 'sum'), ipl_p_balls=('is_batter_ball', 'sum'), ipl_p_outs=('is_batter_out', 'sum'), ipl_p_matches=('match_id', 'nunique')
).reset_index()
df_bat = df_bat.merge(ipl_bat_grp, on='striker_id', how='left').fillna(0)

# 2. T20I under pressure
t20i_bat_grp = t20i_p_bat.groupby('striker_id').agg(
    t20i_p_runs=('runs', 'sum'), t20i_p_balls=('is_batter_ball', 'sum'), t20i_p_outs=('is_batter_out', 'sum'), t20i_p_matches=('match_id', 'nunique')
).reset_index()
df_bat = df_bat.merge(t20i_bat_grp, on='striker_id', how='left').fillna(0)

# Format-specific shrinkage:
# SR shrunk by balls (K_sr = 30.0); Batting Average shrunk by DISMISSALS (K_outs = 5.0) using conjugate prior
K_sr = 30.0
K_outs = 5.0

df_bat['ipl_raw_sr'] = np.where(df_bat['ipl_p_balls'] > 0, (df_bat['ipl_p_runs'] / df_bat['ipl_p_balls']) * 100.0, mu_sr_ipl_bat)
df_bat['ipl_shrunk_sr'] = (df_bat['ipl_p_balls'] / (df_bat['ipl_p_balls'] + K_sr)) * df_bat['ipl_raw_sr'] + (K_sr / (df_bat['ipl_p_balls'] + K_sr)) * mu_sr_ipl_bat
df_bat['ipl_shrunk_avg'] = (df_bat['ipl_p_runs'] + K_outs * mu_avg_ipl_bat) / (df_bat['ipl_p_outs'] + K_outs)

df_bat['t20i_raw_sr'] = np.where(df_bat['t20i_p_balls'] > 0, (df_bat['t20i_p_runs'] / df_bat['t20i_p_balls']) * 100.0, mu_sr_t20i_bat)
df_bat['t20i_shrunk_sr'] = (df_bat['t20i_p_balls'] / (df_bat['t20i_p_balls'] + K_sr)) * df_bat['t20i_raw_sr'] + (K_sr / (df_bat['t20i_p_balls'] + K_sr)) * mu_sr_t20i_bat
df_bat['t20i_shrunk_avg'] = (df_bat['t20i_p_runs'] + K_outs * mu_avg_t20i_bat) / (df_bat['t20i_p_outs'] + K_outs)

# Sample confidence
df_bat['c_ipl'] = 1.0 - np.exp(-df_bat['ipl_p_balls'] / 40.0)
df_bat['c_t20i'] = 1.0 - np.exp(-df_bat['t20i_p_balls'] / 40.0)
df_bat['confidence_score'] = (1.0 - np.exp(-df_bat['pressure_balls'] / 50.0)).round(3)

# Confidence-weighted 70/30 format weights
denom_bat = 0.70 * df_bat['c_ipl'] + 0.30 * df_bat['c_t20i']
df_bat['ipl_weight'] = np.where(
    denom_bat > 0,
    np.where((df_bat['c_ipl'] > 0) & (df_bat['c_t20i'] > 0), (0.70 * df_bat['c_ipl']) / denom_bat,
             np.where(df_bat['c_ipl'] > 0, 1.0, 0.0)),
    0.0
).round(3)
df_bat['t20i_weight'] = np.where(
    denom_bat > 0,
    np.where((df_bat['c_ipl'] > 0) & (df_bat['c_t20i'] > 0), (0.30 * df_bat['c_t20i']) / denom_bat,
             np.where(df_bat['c_t20i'] > 0, 1.0, 0.0)),
    0.0
).round(3)

# Environment normalization: normalizes T20I scoring rates to IPL benchmark par
t20i_sr_env_adj = mu_sr_ipl_bat + (df_bat['t20i_shrunk_sr'] - mu_sr_t20i_bat)
t20i_avg_env_adj = mu_avg_ipl_bat + (df_bat['t20i_shrunk_avg'] - mu_avg_t20i_bat)

# Blended format performance contributions
df_bat['blended_shrunk_sr'] = np.where(
    (df_bat['c_ipl'] > 0) & (df_bat['c_t20i'] > 0),
    df_bat['ipl_weight'] * df_bat['ipl_shrunk_sr'] + df_bat['t20i_weight'] * t20i_sr_env_adj,
    np.where(df_bat['c_ipl'] > 0, df_bat['ipl_shrunk_sr'], t20i_sr_env_adj)
)
df_bat['blended_shrunk_avg'] = np.where(
    (df_bat['c_ipl'] > 0) & (df_bat['c_t20i'] > 0),
    df_bat['ipl_weight'] * df_bat['ipl_shrunk_avg'] + df_bat['t20i_weight'] * t20i_avg_env_adj,
    np.where(df_bat['c_ipl'] > 0, df_bat['ipl_shrunk_avg'], t20i_avg_env_adj)
)

# Personal baseline delta (Resilience)
df_bat['delta_sr'] = df_bat['blended_shrunk_sr'] - df_bat['normal_sr']
quality_mult_bat = np.clip((df_bat['blended_shrunk_sr'] - 120.0) / 40.0, 0.0, 1.0)
df_bat['bounded_delta_sr'] = np.clip(df_bat['delta_sr'], -30.0, 45.0) * quality_mult_bat

# Eligibility: Minimum 60 pressure balls faced and min 8 pressure matches
df_bat['is_eligible'] = (df_bat['pressure_balls'] >= 60) & (df_bat['pressure_matches'] >= 8)

elig_bat = df_bat[df_bat['is_eligible']].copy()
print(f"Eligible batters for Top 10 ranking: {len(elig_bat)} (Total tracked batters: {len(df_bat)})")

# Standardized Z-scores across eligible population
z_sr = safe_zscore(elig_bat['blended_shrunk_sr'])
z_avg = safe_zscore(elig_bat['blended_shrunk_avg'])
z_delta = safe_zscore(elig_bat['bounded_delta_sr'])
z_bdry_dot = safe_zscore(elig_bat['pressure_bdry_pct'] - elig_bat['pressure_dot_pct'])
z_extreme = safe_zscore(np.where(elig_bat['extreme_balls'] >= 15, elig_bat['extreme_sr'], mu_sr_all_bat))
z_consist = safe_zscore(0.60 * elig_bat['match_consistency'] + 0.40 * elig_bat['season_consistency'])
z_comp = safe_zscore(elig_bat['blended_shrunk_sr'] - mu_sr_ipl_bat)

# Composite Clutch Rating (7 components summing to 1.00)
raw_bat_clutch = (
    0.20 * z_sr +
    0.05 * z_avg +
    0.20 * z_delta +
    0.15 * z_bdry_dot +
    0.15 * z_extreme +
    0.15 * z_consist +
    0.10 * z_comp
)

pct_bat = stats.norm.cdf(raw_bat_clutch) * 100.0

# Format calibration factor: 10% IPL difficulty discount for pure T20I players without IPL evidence
format_factor_bat = np.where(elig_bat['c_ipl'] > 0, 1.0, 0.90)
elig_bat['clutch_rating'] = (pct_bat * (0.80 + 0.20 * elig_bat['confidence_score']) * format_factor_bat).round(2)
elig_bat['clutch_rating'] = np.clip(elig_bat['clutch_rating'], 0.0, 99.5)

assert not elig_bat['clutch_rating'].isna().any(), "Batting clutch ratings contain NaNs!"
assert not np.isinf(elig_bat['clutch_rating']).any(), "Batting clutch ratings contain Infs!"

df_bat = df_bat.merge(elig_bat[['striker_id', 'clutch_rating']], on='striker_id', how='left').fillna({'clutch_rating': 0.0})

# -------------------------------------------------------------------------
# BOWLING ANALYTICS & CLUTCH RATING
# -------------------------------------------------------------------------
print("\nCalculating Comprehensive Bowling Metrics...")

bbb_df['is_legal_bowl'] = bbb_df['is_legal_ball']
bbb_df['is_bowler_dot'] = (bbb_df['bowler_runs_conceded'] == 0) & bbb_df['is_legal_ball']
bbb_df['is_bowler_boundary'] = bbb_df['is_four'] | bbb_df['is_six']

p_mask_bowl = bbb_df['bowling_pressure'] >= 50
p_delivs_bowl = bbb_df[p_mask_bowl]

# Format subsets under pressure
ipl_p_bowl = p_delivs_bowl[p_delivs_bowl['is_ipl']]
t20i_p_bowl = p_delivs_bowl[p_delivs_bowl['match_format'] == 'T20I']

# Benchmark population means
mu_econ_all_bowl = (p_delivs_bowl['bowler_runs_conceded'].sum() * 6.0) / p_delivs_bowl['is_legal_bowl'].sum()
mu_wpo_all_bowl = (p_delivs_bowl['is_bowler_wicket'].sum() * 6.0) / p_delivs_bowl['is_legal_bowl'].sum()

mu_econ_ipl_bowl = (ipl_p_bowl['bowler_runs_conceded'].sum() * 6.0) / ipl_p_bowl['is_legal_bowl'].sum()
mu_wpo_ipl_bowl = (ipl_p_bowl['is_bowler_wicket'].sum() * 6.0) / ipl_p_bowl['is_legal_bowl'].sum()

mu_econ_t20i_bowl = (t20i_p_bowl['bowler_runs_conceded'].sum() * 6.0) / t20i_p_bowl['is_legal_bowl'].sum()
mu_wpo_t20i_bowl = (t20i_p_bowl['is_bowler_wicket'].sum() * 6.0) / t20i_p_bowl['is_legal_bowl'].sum()

# Overall aggregates across all deliveries
overall_inns_bowl = bbb_df[['bowler_id', 'match_id', 'innings']].drop_duplicates().groupby('bowler_id').size().rename('overall_innings')
overall_bowl = bbb_df.groupby(['bowler_id', 'bowler_name']).agg(
    overall_runs=('bowler_runs_conceded', 'sum'),
    overall_balls=('is_legal_bowl', 'sum'),
    overall_wickets=('is_bowler_wicket', 'sum'),
    overall_dots=('is_bowler_dot', 'sum'),
    overall_boundaries=('is_bowler_boundary', 'sum'),
    overall_extras=('bowler_extras', 'sum'),
    overall_matches=('match_id', 'nunique'),
).reset_index().merge(overall_inns_bowl, on='bowler_id', how='left')

# Exact bowling rates: runs * 6 / legal_balls (NEVER divide by rounded decimal overs!)
overall_bowl['overall_overs'] = overall_bowl['overall_balls'].apply(to_cricket_overs)
overall_bowl['overall_econ'] = np.where(overall_bowl['overall_balls'] > 0, (overall_bowl['overall_runs'] * 6.0) / overall_bowl['overall_balls'], 12.0)
overall_bowl['overall_wpo'] = np.where(overall_bowl['overall_balls'] > 0, (overall_bowl['overall_wickets'] * 6.0) / overall_bowl['overall_balls'], 0.0)
overall_bowl['overall_sr'] = np.where(overall_bowl['overall_wickets'] > 0, overall_bowl['overall_balls'] / overall_bowl['overall_wickets'], 100.0)

# Pressure aggregates (P >= 50)
p_inns_bowl = p_delivs_bowl[['bowler_id', 'match_id', 'innings']].drop_duplicates().groupby('bowler_id').size().rename('pressure_innings')
p_bowl_grp = p_delivs_bowl.groupby(['bowler_id', 'bowler_name']).agg(
    pressure_runs=('bowler_runs_conceded', 'sum'),
    pressure_balls=('is_legal_bowl', 'sum'),
    pressure_wickets=('is_bowler_wicket', 'sum'),
    pressure_dots=('is_bowler_dot', 'sum'),
    pressure_boundaries=('is_bowler_boundary', 'sum'),
    pressure_extras=('bowler_extras', 'sum'),
    pressure_matches=('match_id', 'nunique'),
).reset_index().merge(p_inns_bowl, on='bowler_id', how='left')

p_bowl_grp['pressure_overs'] = p_bowl_grp['pressure_balls'].apply(to_cricket_overs)
p_bowl_grp['pressure_econ'] = np.where(p_bowl_grp['pressure_balls'] > 0, (p_bowl_grp['pressure_runs'] * 6.0) / p_bowl_grp['pressure_balls'], 12.0)
p_bowl_grp['pressure_wpo'] = np.where(p_bowl_grp['pressure_balls'] > 0, (p_bowl_grp['pressure_wickets'] * 6.0) / p_bowl_grp['pressure_balls'], 0.0)
p_bowl_grp['pressure_sr'] = np.where(p_bowl_grp['pressure_wickets'] > 0, p_bowl_grp['pressure_balls'] / p_bowl_grp['pressure_wickets'], 100.0)
p_bowl_grp['pressure_dot_pct'] = np.where(p_bowl_grp['pressure_balls'] > 0, (p_bowl_grp['pressure_dots'] / p_bowl_grp['pressure_balls']) * 100.0, 0.0)
p_bowl_grp['pressure_bdry_conceded_pct'] = np.where(p_bowl_grp['pressure_balls'] > 0, (p_bowl_grp['pressure_boundaries'] / p_bowl_grp['pressure_balls']) * 100.0, 0.0)

# High pressure (50 <= P < 70)
h_mask_bowl = (bbb_df['bowling_pressure'] >= 50) & (bbb_df['bowling_pressure'] < 70)
h_bowl_grp = bbb_df[h_mask_bowl].groupby(['bowler_id', 'bowler_name']).agg(
    high_runs=('bowler_runs_conceded', 'sum'), high_balls=('is_legal_bowl', 'sum'), high_wickets=('is_bowler_wicket', 'sum')
).reset_index()
h_bowl_grp['high_overs'] = h_bowl_grp['high_balls'].apply(to_cricket_overs)
h_bowl_grp['high_econ'] = np.where(h_bowl_grp['high_balls'] > 0, (h_bowl_grp['high_runs'] * 6.0) / h_bowl_grp['high_balls'], 12.0)

# Extreme pressure (P >= 70)
e_mask_bowl = bbb_df['bowling_pressure'] >= 70
e_bowl_grp = bbb_df[e_mask_bowl].groupby(['bowler_id', 'bowler_name']).agg(
    extreme_runs=('bowler_runs_conceded', 'sum'), extreme_balls=('is_legal_bowl', 'sum'), extreme_wickets=('is_bowler_wicket', 'sum'), extreme_dots=('is_bowler_dot', 'sum')
).reset_index()
e_bowl_grp['extreme_overs'] = e_bowl_grp['extreme_balls'].apply(to_cricket_overs)
e_bowl_grp['extreme_econ'] = np.where(e_bowl_grp['extreme_balls'] > 0, (e_bowl_grp['extreme_runs'] * 6.0) / e_bowl_grp['extreme_balls'], 12.0)

# Normal pressure (P < 50)
n_mask_bowl = bbb_df['bowling_pressure'] < 50
n_bowl_grp = bbb_df[n_mask_bowl].groupby(['bowler_id', 'bowler_name']).agg(
    normal_runs=('bowler_runs_conceded', 'sum'), normal_balls=('is_legal_bowl', 'sum'), normal_wickets=('is_bowler_wicket', 'sum')
).reset_index()
n_bowl_grp['normal_overs'] = n_bowl_grp['normal_balls'].apply(to_cricket_overs)
n_bowl_grp['normal_econ'] = np.where(n_bowl_grp['normal_balls'] > 0, (n_bowl_grp['normal_runs'] * 6.0) / n_bowl_grp['normal_balls'], 12.0)
n_bowl_grp['normal_wpo'] = np.where(n_bowl_grp['normal_balls'] > 0, (n_bowl_grp['normal_wickets'] * 6.0) / n_bowl_grp['normal_balls'], 0.0)

# Merge overall and tier subsets
df_bowl = overall_bowl.merge(p_bowl_grp, on=['bowler_id', 'bowler_name'], how='left').fillna(0)
df_bowl = df_bowl.merge(h_bowl_grp, on=['bowler_id', 'bowler_name'], how='left').fillna(0)
df_bowl = df_bowl.merge(e_bowl_grp, on=['bowler_id', 'bowler_name'], how='left').fillna(0)
df_bowl = df_bowl.merge(n_bowl_grp, on=['bowler_id', 'bowler_name'], how='left').fillna(0)

# Match consistency with Bayesian shrinkage of economy CV towards league prior (0.40)
m_bowl = p_delivs_bowl.groupby(['bowler_id', 'match_id']).agg(r=('bowler_runs_conceded', 'sum'), b=('is_legal_bowl', 'sum')).reset_index()
m_bowl['econ'] = np.where(m_bowl['b'] > 0, (m_bowl['r'] * 6.0) / m_bowl['b'], 12.0)
m_agg_bowl = m_bowl.groupby('bowler_id')['econ'].agg(['std', 'mean', 'count']).reset_index()
m_agg_bowl['raw_cv'] = np.where(m_agg_bowl['mean'] > 0, m_agg_bowl['std'].fillna(2.0) / m_agg_bowl['mean'], 1.0)
m_agg_bowl['shrunk_cv'] = (m_agg_bowl['count'] / (m_agg_bowl['count'] + Km)) * m_agg_bowl['raw_cv'] + (Km / (m_agg_bowl['count'] + Km)) * 0.40
m_agg_bowl['match_consistency'] = np.clip(1.0 - (m_agg_bowl['shrunk_cv']), 0.1, 1.0)
df_bowl = df_bowl.merge(m_agg_bowl[['bowler_id', 'match_consistency']], on='bowler_id', how='left').fillna({'match_consistency': 0.3})

# Season consistency with Bayesian shrinkage
s_bowl = p_delivs_bowl.groupby(['bowler_id', 'season']).agg(r=('bowler_runs_conceded', 'sum'), b=('is_legal_bowl', 'sum')).reset_index()
s_bowl['econ'] = np.where(s_bowl['b'] > 0, (s_bowl['r'] * 6.0) / s_bowl['b'], 12.0)
s_agg_bowl = s_bowl.groupby('bowler_id')['econ'].agg(['std', 'mean', 'count']).reset_index()
s_agg_bowl['raw_cv'] = np.where(s_agg_bowl['mean'] > 0, s_agg_bowl['std'].fillna(2.0) / (s_agg_bowl['mean'] + 1e-5), 1.0)
s_agg_bowl['shrunk_cv'] = (s_agg_bowl['count'] / (s_agg_bowl['count'] + Ks)) * s_agg_bowl['raw_cv'] + (Ks / (s_agg_bowl['count'] + Ks)) * 0.40
s_agg_bowl['season_consistency'] = np.clip(1.0 - (s_agg_bowl['shrunk_cv']), 0.1, 1.0)
df_bowl = df_bowl.merge(s_agg_bowl[['bowler_id', 'season_consistency']], on='bowler_id', how='left').fillna({'season_consistency': 0.3})

# Format-specific aggregates
# 1. IPL under pressure
ipl_bowl_grp = ipl_p_bowl.groupby('bowler_id').agg(
    ipl_p_runs=('bowler_runs_conceded', 'sum'), ipl_p_balls=('is_legal_bowl', 'sum'), ipl_p_wkts=('is_bowler_wicket', 'sum'), ipl_p_matches=('match_id', 'nunique')
).reset_index()
df_bowl = df_bowl.merge(ipl_bowl_grp, on='bowler_id', how='left').fillna(0)

# 2. T20I under pressure
t20i_bowl_grp = t20i_p_bowl.groupby('bowler_id').agg(
    t20i_p_runs=('bowler_runs_conceded', 'sum'), t20i_p_balls=('is_legal_bowl', 'sum'), t20i_p_wkts=('is_bowler_wicket', 'sum'), t20i_p_matches=('match_id', 'nunique')
).reset_index()
df_bowl = df_bowl.merge(t20i_bowl_grp, on='bowler_id', how='left').fillna(0)

# Format-specific shrinkage (K_bowl = 36.0 balls / 6 overs)
K_bowl = 36.0

df_bowl['ipl_raw_econ'] = np.where(df_bowl['ipl_p_balls'] > 0, (df_bowl['ipl_p_runs'] * 6.0) / df_bowl['ipl_p_balls'], mu_econ_ipl_bowl)
df_bowl['ipl_shrunk_econ'] = (df_bowl['ipl_p_balls'] / (df_bowl['ipl_p_balls'] + K_bowl)) * df_bowl['ipl_raw_econ'] + (K_bowl / (df_bowl['ipl_p_balls'] + K_bowl)) * mu_econ_ipl_bowl
df_bowl['ipl_raw_wpo'] = np.where(df_bowl['ipl_p_balls'] > 0, (df_bowl['ipl_p_wkts'] * 6.0) / df_bowl['ipl_p_balls'], mu_wpo_ipl_bowl)
df_bowl['ipl_shrunk_wpo'] = (df_bowl['ipl_p_balls'] / (df_bowl['ipl_p_balls'] + K_bowl)) * df_bowl['ipl_raw_wpo'] + (K_bowl / (df_bowl['ipl_p_balls'] + K_bowl)) * mu_wpo_ipl_bowl

df_bowl['t20i_raw_econ'] = np.where(df_bowl['t20i_p_balls'] > 0, (df_bowl['t20i_p_runs'] * 6.0) / df_bowl['t20i_p_balls'], mu_econ_t20i_bowl)
df_bowl['t20i_shrunk_econ'] = (df_bowl['t20i_p_balls'] / (df_bowl['t20i_p_balls'] + K_bowl)) * df_bowl['t20i_raw_econ'] + (K_bowl / (df_bowl['t20i_p_balls'] + K_bowl)) * mu_econ_t20i_bowl
df_bowl['t20i_raw_wpo'] = np.where(df_bowl['t20i_p_balls'] > 0, (df_bowl['t20i_p_wkts'] * 6.0) / df_bowl['t20i_p_balls'], mu_wpo_t20i_bowl)
df_bowl['t20i_shrunk_wpo'] = (df_bowl['t20i_p_balls'] / (df_bowl['t20i_p_balls'] + K_bowl)) * df_bowl['t20i_raw_wpo'] + (K_bowl / (df_bowl['t20i_p_balls'] + K_bowl)) * mu_wpo_t20i_bowl

# Sample confidence
df_bowl['c_ipl'] = 1.0 - np.exp(-df_bowl['ipl_p_balls'] / 50.0)
df_bowl['c_t20i'] = 1.0 - np.exp(-df_bowl['t20i_p_balls'] / 50.0)
df_bowl['confidence_score'] = (1.0 - np.exp(-df_bowl['pressure_balls'] / 60.0)).round(3)

# Confidence-weighted 70/30 format weights
denom_bowl = 0.70 * df_bowl['c_ipl'] + 0.30 * df_bowl['c_t20i']
df_bowl['ipl_weight'] = np.where(
    denom_bowl > 0,
    np.where((df_bowl['c_ipl'] > 0) & (df_bowl['c_t20i'] > 0), (0.70 * df_bowl['c_ipl']) / denom_bowl,
             np.where(df_bowl['c_ipl'] > 0, 1.0, 0.0)),
    0.0
).round(3)
df_bowl['t20i_weight'] = np.where(
    denom_bowl > 0,
    np.where((df_bowl['c_ipl'] > 0) & (df_bowl['c_t20i'] > 0), (0.30 * df_bowl['c_t20i']) / denom_bowl,
             np.where(df_bowl['c_t20i'] > 0, 1.0, 0.0)),
    0.0
).round(3)

# Environment normalization: normalizes T20I economy & wicket rate to IPL benchmark par
t20i_econ_env_adj = mu_econ_ipl_bowl + (df_bowl['t20i_shrunk_econ'] - mu_econ_t20i_bowl)
t20i_wpo_env_adj = mu_wpo_ipl_bowl + (df_bowl['t20i_shrunk_wpo'] - mu_wpo_t20i_bowl)

# Blended format performance contributions
df_bowl['blended_shrunk_econ'] = np.where(
    (df_bowl['c_ipl'] > 0) & (df_bowl['c_t20i'] > 0),
    df_bowl['ipl_weight'] * df_bowl['ipl_shrunk_econ'] + df_bowl['t20i_weight'] * t20i_econ_env_adj,
    np.where(df_bowl['c_ipl'] > 0, df_bowl['ipl_shrunk_econ'], t20i_econ_env_adj)
)
df_bowl['blended_shrunk_wpo'] = np.where(
    (df_bowl['c_ipl'] > 0) & (df_bowl['c_t20i'] > 0),
    df_bowl['ipl_weight'] * df_bowl['ipl_shrunk_wpo'] + df_bowl['t20i_weight'] * t20i_wpo_env_adj,
    np.where(df_bowl['c_ipl'] > 0, df_bowl['ipl_shrunk_wpo'], t20i_wpo_env_adj)
)

# Personal baseline delta (Expectation-adjusted resilience)
expected_p_econ = df_bowl['normal_econ'] + 1.30
df_bowl['delta_econ'] = expected_p_econ - df_bowl['blended_shrunk_econ']
quality_mult_bowl = np.clip((10.5 - df_bowl['blended_shrunk_econ']) / 2.5, 0.0, 1.0)
df_bowl['bounded_delta_econ'] = np.clip(df_bowl['delta_econ'], -2.0, 3.5) * quality_mult_bowl

# Eligibility: Minimum 90 pressure balls bowled (15.0 overs) and min 10 pressure matches
df_bowl['is_eligible'] = (df_bowl['pressure_balls'] >= 90) & (df_bowl['pressure_matches'] >= 10)

elig_bowl = df_bowl[df_bowl['is_eligible']].copy()
print(f"Eligible bowlers for Top 10 ranking: {len(elig_bowl)} (Total tracked bowlers: {len(df_bowl)})")

# Standardized Z-scores across eligible population
z_econ = -safe_zscore(elig_bowl['blended_shrunk_econ'])  # Lower economy is better
z_wpo = safe_zscore(elig_bowl['blended_shrunk_wpo'])     # Higher wicket rate is better
z_delta_bowl = safe_zscore(elig_bowl['bounded_delta_econ'])
z_dot_bdry_bowl = safe_zscore(elig_bowl['pressure_dot_pct'] - elig_bowl['pressure_bdry_conceded_pct'])
z_extreme_bowl = -safe_zscore(np.where(elig_bowl['extreme_balls'] >= 18, elig_bowl['extreme_econ'], mu_econ_all_bowl))
z_consist_bowl = safe_zscore(0.60 * elig_bowl['match_consistency'] + 0.40 * elig_bowl['season_consistency'])
z_comp_bowl = safe_zscore(mu_econ_ipl_bowl - elig_bowl['blended_shrunk_econ'])

# Composite Clutch Rating (Explicit 7 components summing to 1.00)
raw_bowl_clutch = (
    0.20 * z_econ +
    0.20 * z_wpo +
    0.15 * z_delta_bowl +
    0.15 * z_dot_bdry_bowl +
    0.10 * z_extreme_bowl +
    0.10 * z_consist_bowl +
    0.10 * z_comp_bowl
)

pct_bowl = stats.norm.cdf(raw_bowl_clutch) * 100.0

# Format calibration factor: 10% IPL difficulty discount for pure T20I players without IPL evidence
format_factor_bowl = np.where(elig_bowl['c_ipl'] > 0, 1.0, 0.90)
elig_bowl['clutch_rating'] = (pct_bowl * (0.80 + 0.20 * elig_bowl['confidence_score']) * format_factor_bowl).round(2)
elig_bowl['clutch_rating'] = np.clip(elig_bowl['clutch_rating'], 0.0, 99.5)

assert not elig_bowl['clutch_rating'].isna().any(), "Bowling clutch ratings contain NaNs!"
assert not np.isinf(elig_bowl['clutch_rating']).any(), "Bowling clutch ratings contain Infs!"

df_bowl = df_bowl.merge(elig_bowl[['bowler_id', 'clutch_rating']], on='bowler_id', how='left').fillna({'clutch_rating': 0.0})

# -------------------------------------------------------------------------
# GENERATE DELIVERABLES & OUTPUT FILES
# -------------------------------------------------------------------------
print("\n" + "="*70)
print("FINAL TOP 10 BATTERS UNDER PRESSURE")
print("="*70)
final_top10_bat = df_bat[df_bat['is_eligible']].sort_values('clutch_rating', ascending=False).head(10).reset_index(drop=True)
final_top10_bat['Rank'] = range(1, 11)

# Rename columns for clear presentation matching specification
top10_bat_export = final_top10_bat[[
    'Rank', 'striker_name', 'striker_id', 'clutch_rating',
    'overall_runs', 'overall_balls', 'overall_sr', 'overall_avg',
    'pressure_runs', 'pressure_balls', 'pressure_sr', 'pressure_avg',
    'normal_sr', 'delta_sr', 'extreme_sr', 'pressure_bdry_pct', 'pressure_dot_pct',
    'ipl_weight', 't20i_weight', 'confidence_score', 'pressure_matches'
]].copy()
top10_bat_export.columns = [
    'Rank', 'Player_Name', 'Player_ID', 'clutch_rating',
    'overall_runs', 'overall_balls', 'overall_sr', 'overall_avg',
    'pressure_runs', 'pressure_balls', 'pressure_sr', 'pressure_avg',
    'normal_sr', 'delta_sr', 'extreme_sr', 'pressure_bdry_pct', 'pressure_dot_pct',
    'ipl_weight', 't20i_weight', 'confidence_score', 'pressure_matches'
]

print(top10_bat_export[['Rank', 'Player_Name', 'Player_ID', 'clutch_rating', 'pressure_sr', 'pressure_avg', 'delta_sr', 'ipl_weight', 'pressure_balls']])

print("\n" + "="*70)
print("FINAL TOP 10 BOWLERS UNDER PRESSURE")
print("="*70)
final_top10_bowl = df_bowl[df_bowl['is_eligible']].sort_values('clutch_rating', ascending=False).head(10).reset_index(drop=True)
final_top10_bowl['Rank'] = range(1, 11)

top10_bowl_export = final_top10_bowl[[
    'Rank', 'bowler_name', 'bowler_id', 'clutch_rating',
    'overall_overs', 'overall_balls', 'overall_econ', 'overall_wickets', 'overall_wpo',
    'pressure_overs', 'pressure_balls', 'pressure_econ', 'pressure_wickets', 'pressure_wpo',
    'normal_econ', 'delta_econ', 'extreme_econ', 'pressure_dot_pct', 'pressure_bdry_conceded_pct',
    'ipl_weight', 't20i_weight', 'confidence_score', 'pressure_matches'
]].copy()
top10_bowl_export.columns = [
    'Rank', 'Player_Name', 'Player_ID', 'clutch_rating',
    'overall_overs', 'overall_balls', 'overall_econ', 'overall_wickets', 'overall_wpo',
    'pressure_overs', 'pressure_balls', 'pressure_econ', 'pressure_wickets', 'pressure_wpo',
    'normal_econ', 'delta_econ', 'extreme_econ', 'pressure_dot_pct', 'pressure_bdry_conceded_pct',
    'ipl_weight', 't20i_weight', 'confidence_score', 'pressure_matches'
]

print(top10_bowl_export[['Rank', 'Player_Name', 'Player_ID', 'clutch_rating', 'pressure_overs', 'pressure_econ', 'pressure_wickets', 'pressure_wpo', 'ipl_weight', 'pressure_balls']])

# Export Top 10 CSVs
top10_bat_export.to_csv('output/Top_10_Batters.csv', index=False)
top10_bowl_export.to_csv('output/Top_10_Bowlers.csv', index=False)

# Export All_Player_Scores.csv
all_scores_bat = df_bat[['striker_id', 'striker_name', 'clutch_rating', 'is_eligible', 'overall_runs', 'overall_sr', 'pressure_runs', 'pressure_balls', 'pressure_sr', 'ipl_weight', 'confidence_score']].copy()
all_scores_bat.columns = ['player_id', 'player_name', 'batting_clutch_rating', 'is_bat_eligible', 'overall_runs', 'overall_sr', 'pressure_runs', 'pressure_balls', 'pressure_sr', 'bat_ipl_weight', 'bat_confidence']

all_scores_bowl = df_bowl[['bowler_id', 'bowler_name', 'clutch_rating', 'is_eligible', 'overall_overs', 'overall_econ', 'pressure_overs', 'pressure_balls', 'pressure_econ', 'pressure_wickets', 'ipl_weight', 'confidence_score']].copy()
all_scores_bowl.columns = ['player_id', 'player_name', 'bowling_clutch_rating', 'is_bowl_eligible', 'overall_overs', 'overall_econ', 'pressure_overs', 'pressure_balls', 'pressure_econ', 'pressure_wickets', 'bowl_ipl_weight', 'bowl_confidence']

all_player_scores = all_scores_bat.merge(all_scores_bowl, on=['player_id', 'player_name'], how='outer').fillna(0)
all_player_scores.to_csv('output/All_Player_Scores.csv', index=False)

# Export Player_Performance_Summary.csv
perf_summary = all_player_scores.sort_values(by=['batting_clutch_rating', 'bowling_clutch_rating'], ascending=False)
perf_summary.to_csv('output/Player_Performance_Summary.csv', index=False)

print("\nFiles successfully created in output/:")
print("- output/Top_10_Batters.csv")
print("- output/Top_10_Bowlers.csv")
print("- output/All_Player_Scores.csv")
print("- output/Player_Performance_Summary.csv")
print("- output/Pressure_Delivery_Analysis.csv")
