import os
import sys
import pandas as pd
import numpy as np
from scipy import stats

print("=" * 70)
print("COMPUTING CLUTCH RATINGS & PLAYER ANALYTICS")
print("=" * 70)

# Import modeled deliveries from model_pressure
from model_pressure import bbb_df, matches_df

# Load competition mapping to identify formats and seasons
comp_df = pd.read_csv('Data Pack/competitions.csv')
p11_df = pd.read_csv('Data Pack/playing_eleven.csv')
mapping_df = pd.read_csv('Data Pack/competition_team_player_mapping.csv')

# Merge match format and season onto bbb_df
matches_meta = matches_df[['match_id', 'comp_id']].merge(comp_df[['comp_id', 'comp_name', 'match_format', 'season']], on='comp_id', how='left')
bbb_df = bbb_df.merge(matches_meta[['match_id', 'comp_name', 'match_format', 'season']], on='match_id', how='left')
bbb_df['is_ipl'] = bbb_df['comp_name'].str.contains('IPL', na=False)

print(f"Total deliveries with metadata: {len(bbb_df):,}")

# -------------------------------------------------------------------------
# BATTING ANALYTICS ENGINE
# -------------------------------------------------------------------------
print("\nProcessing Batting Analytics...")

# Balls faced by batter: non-wides
bbb_df['is_batter_ball'] = (bbb_df['extras_type'] != 'wide')
# Batter dismissal
bbb_df['is_batter_out'] = (bbb_df['is_wicket'] == True) & (bbb_df['dismissed_player_id'] == bbb_df['striker_id'])

# Helper for aggregation
def compute_batting_stats(df_subset, prefix=''):
    grouped = df_subset.groupby(['striker_id', 'striker_name'])
    res = grouped.agg(
        runs=( 'runs', 'sum'),
        balls_faced=('is_batter_ball', 'sum'),
        outs=('is_batter_out', 'sum'),
        fours=('is_four', 'sum'),
        sixes=('is_six', 'sum'),
        dots=('runs', lambda x: (x == 0).sum()),
        matches=('match_id', 'nunique'),
        innings_batted=('match_id', lambda x: df_subset.loc[x.index, ['match_id', 'innings']].drop_duplicates().shape[0])
    ).reset_index()
    
    res[f'{prefix}runs'] = res['runs']
    res[f'{prefix}balls'] = res['balls_faced']
    res[f'{prefix}outs'] = res['outs']
    res[f'{prefix}fours'] = res['fours']
    res[f'{prefix}sixes'] = res['sixes']
    res[f'{prefix}dots'] = res['dots']
    res[f'{prefix}matches'] = res['matches']
    res[f'{prefix}innings'] = res['innings_batted']
    
    res[f'{prefix}sr'] = np.where(res[f'{prefix}balls'] > 0, (res[f'{prefix}runs'] / res[f'{prefix}balls']) * 100.0, 0.0)
    res[f'{prefix}avg'] = np.where(res[f'{prefix}outs'] > 0, res[f'{prefix}runs'] / res[f'{prefix}outs'], res[f'{prefix}runs'])
    res[f'{prefix}bdry_pct'] = np.where(res[f'{prefix}balls'] > 0, ((res[f'{prefix}fours'] + res[f'{prefix}sixes']) / res[f'{prefix}balls']) * 100.0, 0.0)
    res[f'{prefix}dot_pct'] = np.where(res[f'{prefix}balls'] > 0, (res[f'{prefix}dots'] / res[f'{prefix}balls']) * 100.0, 0.0)
    res[f'{prefix}dismissal_rate'] = np.where(res[f'{prefix}balls'] > 0, (res[f'{prefix}outs'] / res[f'{prefix}balls']) * 100.0, 0.0)
    
    keep_cols = ['striker_id', 'striker_name'] + [c for c in res.columns if c.startswith(prefix)]
    return res[keep_cols]

# 1. Overall Batting
overall_bat = compute_batting_stats(bbb_df, prefix='overall_')

# 2. Pressure Batting (Pressure >= 50)
pressure_mask = (bbb_df['batting_pressure'] >= 50)
pressure_bat = compute_batting_stats(bbb_df[pressure_mask], prefix='pressure_')

# 3. High Pressure (50 <= Pressure < 70)
high_mask = (bbb_df['batting_pressure'] >= 50) & (bbb_df['batting_pressure'] < 70)
high_bat = compute_batting_stats(bbb_df[high_mask], prefix='high_')

# 4. Extreme Pressure (Pressure >= 70)
extreme_mask = (bbb_df['batting_pressure'] >= 70)
extreme_bat = compute_batting_stats(bbb_df[extreme_mask], prefix='extreme_')

# 5. Normal Batting (Pressure < 50)
normal_mask = (bbb_df['batting_pressure'] < 50)
normal_bat = compute_batting_stats(bbb_df[normal_mask], prefix='normal_')

# 6. IPL-only Pressure Batting
ipl_pressure_bat = compute_batting_stats(bbb_df[pressure_mask & bbb_df['is_ipl']], prefix='ipl_pressure_')

# 7. T20I-only Pressure Batting
t20i_pressure_bat = compute_batting_stats(bbb_df[pressure_mask & (bbb_df['match_format'] == 'T20I')], prefix='t20i_pressure_')

# Merge all batting metrics
bat_df = overall_bat.merge(pressure_bat, on=['striker_id', 'striker_name'], how='left')
bat_df = bat_df.merge(high_bat, on=['striker_id', 'striker_name'], how='left')
bat_df = bat_df.merge(extreme_bat, on=['striker_id', 'striker_name'], how='left')
bat_df = bat_df.merge(normal_bat, on=['striker_id', 'striker_name'], how='left')
bat_df = bat_df.merge(ipl_pressure_bat, on=['striker_id', 'striker_name'], how='left')
bat_df = bat_df.merge(t20i_pressure_bat, on=['striker_id', 'striker_name'], how='left')

# Fill NaNs for splits where player had 0 balls
for col in bat_df.columns:
    if col not in ['striker_id', 'striker_name']:
        bat_df[col] = bat_df[col].fillna(0.0)

# Personal Baseline Deltas
bat_df['delta_sr'] = bat_df['pressure_sr'] - bat_df['normal_sr']
bat_df['delta_avg'] = bat_df['pressure_avg'] - bat_df['normal_avg']

# Match-to-match consistency in pressure situations
# Measure coefficient of variation of runs scored per pressure match
match_p_runs = bbb_df[pressure_mask].groupby(['striker_id', 'match_id'])['runs'].sum().reset_index()
match_p_std = match_p_runs.groupby('striker_id')['runs'].agg(['std', 'mean', 'count']).reset_index()
match_p_std['bat_cv'] = np.where(match_p_std['mean'] > 0, match_p_std['std'] / match_p_std['mean'], 1.5)
match_p_std['bat_consistency'] = np.clip(1.0 - (match_p_std['bat_cv'] / 2.0), 0.1, 1.0)
bat_df = bat_df.merge(match_p_std[['striker_id', 'bat_consistency']], on='striker_id', how='left').fillna({'bat_consistency': 0.3})

# Empirical Bayesian Shrinkage for Batting
comp_pressure_sr = bbb_df[pressure_mask]['runs'].sum() / max(1, bbb_df[pressure_mask]['is_batter_ball'].sum()) * 100.0
comp_pressure_avg = bbb_df[pressure_mask]['runs'].sum() / max(1, bbb_df[pressure_mask]['is_batter_out'].sum())
K_bat = 30.0

bat_df['shrunk_pressure_sr'] = (bat_df['pressure_balls'] / (bat_df['pressure_balls'] + K_bat)) * bat_df['pressure_sr'] + (K_bat / (bat_df['pressure_balls'] + K_bat)) * comp_pressure_sr
bat_df['shrunk_pressure_avg'] = (bat_df['pressure_balls'] / (bat_df['pressure_balls'] + K_bat)) * bat_df['pressure_avg'] + (K_bat / (bat_df['pressure_balls'] + K_bat)) * comp_pressure_avg
bat_df['bat_confidence'] = 1.0 - np.exp(-bat_df['pressure_balls'] / 50.0)

# Eligibility filter: Minimum 50 pressure balls faced
# (We retain all players in All_Player_Scores.csv, but mark eligible for Top 10)
bat_df['is_eligible'] = (bat_df['pressure_balls'] >= 50) & (bat_df['overall_balls'] >= 80)
print(f"Eligible Batters count: {bat_df['is_eligible'].sum()} out of {len(bat_df)}")

# Standardized Z-Scores for Batting Clutch Rating (calculated among eligible pool)
elig_bat = bat_df[bat_df['is_eligible']].copy()

z_sr = stats.zscore(elig_bat['shrunk_pressure_sr'])
z_delta = stats.zscore(elig_bat['delta_sr'])
z_bdry_dot = stats.zscore(elig_bat['pressure_bdry_pct'] - elig_bat['pressure_dot_pct'])
z_extreme = stats.zscore(np.where(elig_bat['extreme_balls'] > 0, elig_bat['extreme_sr'], comp_pressure_sr))
z_consist = stats.zscore(elig_bat['bat_consistency'])
z_avg = stats.zscore(elig_bat['shrunk_pressure_avg'])

# Batting Weights:
# Scoring: 25% (20% SR + 5% Avg)
# Baseline Improvement: 20% (Delta SR)
# Boundary & Dot Efficiency: 15%
# Extreme Pressure: 15%
# Match Consistency: 15%
# Competition-Relative Performance: 10% (Overall Pressure Score)
raw_bat_clutch = (
    0.20 * z_sr +
    0.05 * z_avg +
    0.20 * z_delta +
    0.15 * z_bdry_dot +
    0.15 * z_extreme +
    0.15 * z_consist +
    0.10 * z_sr
)

# Scale to 0-100 via percentile/logistic CDF
clutch_scale_bat = stats.norm.cdf(raw_bat_clutch) * 100.0
# Blend with sample confidence so small samples don't leapfrog consistent performers
elig_bat['clutch_rating'] = (clutch_scale_bat * (0.80 + 0.20 * elig_bat['bat_confidence'])).round(2)

bat_df = bat_df.merge(elig_bat[['striker_id', 'clutch_rating']], on='striker_id', how='left').fillna({'clutch_rating': 0.0})

# -------------------------------------------------------------------------
# BOWLING ANALYTICS ENGINE
# -------------------------------------------------------------------------
print("\nProcessing Bowling Analytics...")

# Legal balls bowled
bbb_df['is_legal_bowl'] = bbb_df['is_legal_ball']
# Dot balls for bowler: runs conceded == 0
bbb_df['is_bowler_dot'] = (bbb_df['bowler_runs_conceded'] == 0) & bbb_df['is_legal_ball']
# Boundary conceded
bbb_df['is_bowler_boundary'] = bbb_df['is_four'] | bbb_df['is_six']

def compute_bowling_stats(df_subset, prefix=''):
    grouped = df_subset.groupby(['bowler_id', 'bowler_name'])
    res = grouped.agg(
        runs_conceded=('bowler_runs_conceded', 'sum'),
        legal_balls=('is_legal_bowl', 'sum'),
        wickets=('is_bowler_wicket', 'sum'),
        dots=('is_bowler_dot', 'sum'),
        boundaries=('is_bowler_boundary', 'sum'),
        extras_conceded=('bowler_extras', 'sum'),
        matches=('match_id', 'nunique'),
        innings_bowled=('match_id', lambda x: df_subset.loc[x.index, ['match_id', 'innings']].drop_duplicates().shape[0])
    ).reset_index()
    
    res[f'{prefix}runs'] = res['runs_conceded']
    res[f'{prefix}balls'] = res['legal_balls']
    res[f'{prefix}wickets'] = res['wickets']
    res[f'{prefix}overs'] = res[f'{prefix}balls'] / 6.0
    res[f'{prefix}dots'] = res['dots']
    res[f'{prefix}boundaries'] = res['boundaries']
    res[f'{prefix}extras'] = res['extras_conceded']
    res[f'{prefix}matches'] = res['matches']
    res[f'{prefix}innings'] = res['innings_bowled']
    
    res[f'{prefix}econ'] = np.where(res[f'{prefix}overs'] > 0, res[f'{prefix}runs'] / res[f'{prefix}overs'], 12.0)
    res[f'{prefix}sr'] = np.where(res[f'{prefix}wickets'] > 0, res[f'{prefix}balls'] / res[f'{prefix}wickets'], 100.0)
    res[f'{prefix}wpo'] = np.where(res[f'{prefix}overs'] > 0, res[f'{prefix}wickets'] / res[f'{prefix}overs'], 0.0)
    res[f'{prefix}dot_pct'] = np.where(res[f'{prefix}balls'] > 0, (res[f'{prefix}dots'] / res[f'{prefix}balls']) * 100.0, 0.0)
    res[f'{prefix}bdry_conceded_pct'] = np.where(res[f'{prefix}balls'] > 0, (res[f'{prefix}boundaries'] / res[f'{prefix}balls']) * 100.0, 0.0)
    
    keep_cols = ['bowler_id', 'bowler_name'] + [c for c in res.columns if c.startswith(prefix)]
    return res[keep_cols]

# 1. Overall Bowling
overall_bowl = compute_bowling_stats(bbb_df, prefix='overall_')

# 2. Pressure Bowling (Pressure >= 50)
bowl_pressure_mask = (bbb_df['bowling_pressure'] >= 50)
pressure_bowl = compute_bowling_stats(bbb_df[bowl_pressure_mask], prefix='pressure_')

# 3. High Pressure (50 <= Pressure < 70)
high_bowl_mask = (bbb_df['bowling_pressure'] >= 50) & (bbb_df['bowling_pressure'] < 70)
high_bowl = compute_bowling_stats(bbb_df[high_bowl_mask], prefix='high_')

# 4. Extreme Pressure (Pressure >= 70)
extreme_bowl_mask = (bbb_df['bowling_pressure'] >= 70)
extreme_bowl = compute_bowling_stats(bbb_df[extreme_bowl_mask], prefix='extreme_')

# 5. Normal Bowling (Pressure < 50)
normal_bowl_mask = (bbb_df['bowling_pressure'] < 50)
normal_bowl = compute_bowling_stats(bbb_df[normal_bowl_mask], prefix='normal_')

# 6. IPL-only Pressure Bowling
ipl_pressure_bowl = compute_bowling_stats(bbb_df[bowl_pressure_mask & bbb_df['is_ipl']], prefix='ipl_pressure_')

# 7. T20I-only Pressure Bowling
t20i_pressure_bowl = compute_bowling_stats(bbb_df[bowl_pressure_mask & (bbb_df['match_format'] == 'T20I')], prefix='t20i_pressure_')

# Merge all bowling metrics
bowl_df = overall_bowl.merge(pressure_bowl, on=['bowler_id', 'bowler_name'], how='left')
bowl_df = bowl_df.merge(high_bowl, on=['bowler_id', 'bowler_name'], how='left')
bowl_df = bowl_df.merge(extreme_bowl, on=['bowler_id', 'bowler_name'], how='left')
bowl_df = bowl_df.merge(normal_bowl, on=['bowler_id', 'bowler_name'], how='left')
bowl_df = bowl_df.merge(ipl_pressure_bowl, on=['bowler_id', 'bowler_name'], how='left')
bowl_df = bowl_df.merge(t20i_pressure_bowl, on=['bowler_id', 'bowler_name'], how='left')

for col in bowl_df.columns:
    if col not in ['bowler_id', 'bowler_name']:
        bowl_df[col] = bowl_df[col].fillna(0.0)

# Personal Baseline Deltas (Positive delta is good)
bowl_df['delta_econ'] = bowl_df['normal_econ'] - bowl_df['pressure_econ']  # Higher is better (tightened up)
bowl_df['delta_wpo'] = bowl_df['pressure_wpo'] - bowl_df['normal_wpo']    # Higher is better

# Match-to-match consistency for bowlers
# Standard deviation of match-level economy under pressure
match_p_bowl = bbb_df[bowl_pressure_mask].groupby(['bowler_id', 'match_id']).agg(
    r=('bowler_runs_conceded', 'sum'),
    b=('is_legal_bowl', 'sum')
).reset_index()
match_p_bowl['econ'] = np.where(match_p_bowl['b'] > 0, (match_p_bowl['r'] / match_p_bowl['b']) * 6.0, 12.0)
bowl_std = match_p_bowl.groupby('bowler_id')['econ'].agg(['std', 'count']).reset_index()
bowl_std['bowl_consistency'] = np.clip(1.0 - (bowl_std['std'].fillna(3.0) / 6.0), 0.1, 1.0)
bowl_df = bowl_df.merge(bowl_std[['bowler_id', 'bowl_consistency']], on='bowler_id', how='left').fillna({'bowl_consistency': 0.3})

# Empirical Bayesian Shrinkage for Bowling
comp_pressure_econ = (bbb_df[bowl_pressure_mask]['bowler_runs_conceded'].sum() / (bbb_df[bowl_pressure_mask]['is_legal_bowl'].sum() / 6.0))
comp_pressure_wpo = (bbb_df[bowl_pressure_mask]['is_bowler_wicket'].sum() / (bbb_df[bowl_pressure_mask]['is_legal_bowl'].sum() / 6.0))
K_bowl = 36.0

bowl_df['shrunk_pressure_econ'] = (bowl_df['pressure_balls'] / (bowl_df['pressure_balls'] + K_bowl)) * bowl_df['pressure_econ'] + (K_bowl / (bowl_df['pressure_balls'] + K_bowl)) * comp_pressure_econ
bowl_df['shrunk_pressure_wpo'] = (bowl_df['pressure_balls'] / (bowl_df['pressure_balls'] + K_bowl)) * bowl_df['pressure_wpo'] + (K_bowl / (bowl_df['pressure_balls'] + K_bowl)) * comp_pressure_wpo
bowl_df['bowl_confidence'] = 1.0 - np.exp(-bowl_df['pressure_balls'] / 60.0)

# Eligibility filter: Minimum 60 pressure legal balls bowled (10 pressure overs)
bowl_df['is_eligible'] = (bowl_df['pressure_balls'] >= 60) & (bowl_df['overall_balls'] >= 100)
print(f"Eligible Bowlers count: {bowl_df['is_eligible'].sum()} out of {len(bowl_df)}")

# Standardized Z-Scores for Bowling Clutch Rating
elig_bowl = bowl_df[bowl_df['is_eligible']].copy()

z_econ = -stats.zscore(elig_bowl['shrunk_pressure_econ'])  # Inverted: lower economy is better!
z_wpo = stats.zscore(elig_bowl['shrunk_pressure_wpo'])     # Higher wicket rate is better!
z_delta_econ = stats.zscore(elig_bowl['delta_econ'])
z_dot_bdry = stats.zscore(elig_bowl['pressure_dot_pct'] - elig_bowl['pressure_bdry_conceded_pct'])
z_extreme_econ = -stats.zscore(np.where(elig_bowl['extreme_balls'] > 0, elig_bowl['extreme_econ'], comp_pressure_econ))
z_bowl_consist = stats.zscore(elig_bowl['bowl_consistency'])

# Bowling Weights:
# Pressure Economy Effectiveness: 25%
# Pressure Wicket-Taking Effectiveness: 20%
# Improvement Relative to Personal Baseline: 15%
# Dot-Ball and Boundary Prevention: 15%
# Match Consistency: 15%
# Competition-Relative Performance: 10%
raw_bowl_clutch = (
    0.25 * z_econ +
    0.20 * z_wpo +
    0.15 * z_delta_econ +
    0.15 * z_dot_bdry +
    0.15 * z_extreme_econ +
    0.10 * z_bowl_consist
)

clutch_scale_bowl = stats.norm.cdf(raw_bowl_clutch) * 100.0
elig_bowl['clutch_rating'] = (clutch_scale_bowl * (0.80 + 0.20 * elig_bowl['bowl_confidence'])).round(2)

bowl_df = bowl_df.merge(elig_bowl[['bowler_id', 'clutch_rating']], on='bowler_id', how='left').fillna({'clutch_rating': 0.0})

# -------------------------------------------------------------------------
# PRELIMINARY TOP 10 RANKINGS INSPECTION
# -------------------------------------------------------------------------
print("\n" + "="*70)
print("PRELIMINARY TOP 10 BATTERS UNDER PRESSURE")
print("="*70)
top_batters = bat_df[bat_df['is_eligible']].sort_values('clutch_rating', ascending=False).head(10).reset_index(drop=True)
top_batters['Rank'] = range(1, 11)
print(top_batters[['Rank', 'striker_name', 'striker_id', 'clutch_rating', 'overall_runs', 'overall_sr', 'pressure_runs', 'pressure_balls', 'pressure_sr', 'delta_sr', 'extreme_sr']])

print("\n" + "="*70)
print("PRELIMINARY TOP 10 BOWLERS UNDER PRESSURE")
print("="*70)
top_bowlers = bowl_df[bowl_df['is_eligible']].sort_values('clutch_rating', ascending=False).head(10).reset_index(drop=True)
top_bowlers['Rank'] = range(1, 11)
print(top_bowlers[['Rank', 'bowler_name', 'bowler_id', 'clutch_rating', 'overall_overs', 'overall_econ', 'overall_wickets', 'pressure_overs', 'pressure_econ', 'pressure_wickets', 'delta_econ']])

