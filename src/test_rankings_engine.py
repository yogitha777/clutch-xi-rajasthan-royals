import sys
import pandas as pd
import numpy as np
from scipy import stats

from model_pressure import bbb_df, matches_df

# Batting setup
bbb_df['is_batter_ball'] = (bbb_df['extras_type'] != 'wide')
bbb_df['is_batter_out'] = (bbb_df['is_wicket'] == True) & (bbb_df['dismissed_player_id'] == bbb_df['striker_id'])

# Bowling setup
bbb_df['is_legal_bowl'] = bbb_df['is_legal_ball']
bbb_df['is_bowler_dot'] = (bbb_df['bowler_runs_conceded'] == 0) & bbb_df['is_legal_ball']
bbb_df['is_bowler_boundary'] = bbb_df['is_four'] | bbb_df['is_six']

def evaluate_format_batting(df_delivs, comp_name='ALL'):
    p_mask = df_delivs['batting_pressure'] >= 50
    norm_mask = df_delivs['batting_pressure'] < 50
    ext_mask = df_delivs['batting_pressure'] >= 70
    
    # Aggregations
    p_grp = df_delivs[p_mask].groupby(['striker_id', 'striker_name']).agg(
        p_runs=('runs', 'sum'),
        p_balls=('is_batter_ball', 'sum'),
        p_outs=('is_batter_out', 'sum'),
        p_fours=('is_four', 'sum'),
        p_sixes=('is_six', 'sum'),
        p_dots=('runs', lambda x: (x == 0).sum()),
        p_matches=('match_id', 'nunique')
    ).reset_index()
    
    norm_grp = df_delivs[norm_mask].groupby(['striker_id', 'striker_name']).agg(
        norm_runs=('runs', 'sum'),
        norm_balls=('is_batter_ball', 'sum'),
        norm_outs=('is_batter_out', 'sum')
    ).reset_index()
    
    ext_grp = df_delivs[ext_mask].groupby(['striker_id', 'striker_name']).agg(
        ext_runs=('runs', 'sum'),
        ext_balls=('is_batter_ball', 'sum'),
        ext_outs=('is_batter_out', 'sum')
    ).reset_index()
    
    merged = p_grp.merge(norm_grp, on=['striker_id', 'striker_name'], how='left').fillna(0)
    merged = merged.merge(ext_grp, on=['striker_id', 'striker_name'], how='left').fillna(0)
    
    merged['p_sr'] = np.where(merged['p_balls'] > 0, (merged['p_runs'] / merged['p_balls']) * 100.0, 0.0)
    merged['p_avg'] = np.where(merged['p_outs'] > 0, merged['p_runs'] / merged['p_outs'], merged['p_runs'])
    merged['norm_sr'] = np.where(merged['norm_balls'] > 0, (merged['norm_runs'] / merged['norm_balls']) * 100.0, 0.0)
    merged['ext_sr'] = np.where(merged['ext_balls'] > 0, (merged['ext_runs'] / merged['ext_balls']) * 100.0, 0.0)
    
    # Robust baseline delta: bounded and conditioned on performing at least at 130 SR
    raw_delta_sr = np.clip(merged['p_sr'] - merged['norm_sr'], -40.0, 50.0)
    quality_mult = np.clip((merged['p_sr'] - 125.0) / 35.0, 0.0, 1.0)
    merged['delta_sr'] = raw_delta_sr * quality_mult
    
    merged['p_bdry_pct'] = np.where(merged['p_balls'] > 0, ((merged['p_fours'] + merged['p_sixes']) / merged['p_balls']) * 100.0, 0.0)
    merged['p_dot_pct'] = np.where(merged['p_balls'] > 0, (merged['p_dots'] / merged['p_balls']) * 100.0, 0.0)
    
    # Match consistency
    match_runs = df_delivs[p_mask].groupby(['striker_id', 'match_id'])['runs'].sum().reset_index()
    m_stats = match_runs.groupby('striker_id')['runs'].agg(['std', 'mean']).reset_index()
    m_stats['cv'] = np.where(m_stats['mean'] > 0, m_stats['std'] / m_stats['mean'], 1.5)
    m_stats['consistency'] = np.clip(1.0 - (m_stats['cv'] / 2.0), 0.1, 1.0)
    merged = merged.merge(m_stats[['striker_id', 'consistency']], on='striker_id', how='left').fillna({'consistency': 0.3})
    
    # Shrinkage
    mu_sr = (df_delivs[p_mask]['runs'].sum() / max(1, df_delivs[p_mask]['is_batter_ball'].sum())) * 100.0
    mu_avg = df_delivs[p_mask]['runs'].sum() / max(1, df_delivs[p_mask]['is_batter_out'].sum())
    K = 30.0
    
    merged['shrunk_p_sr'] = (merged['p_balls'] / (merged['p_balls'] + K)) * merged['p_sr'] + (K / (merged['p_balls'] + K)) * mu_sr
    merged['shrunk_p_avg'] = (merged['p_balls'] / (merged['p_balls'] + K)) * merged['p_avg'] + (K / (merged['p_balls'] + K)) * mu_avg
    merged['confidence'] = 1.0 - np.exp(-merged['p_balls'] / 50.0)
    
    # Standardize
    z_sr = stats.zscore(merged['shrunk_p_sr'])
    z_delta = stats.zscore(merged['delta_sr'])
    z_bdry = stats.zscore(merged['p_bdry_pct'] - merged['p_dot_pct'])
    z_ext = stats.zscore(np.where(merged['ext_balls'] > 0, merged['ext_sr'], mu_sr))
    z_cons = stats.zscore(merged['consistency'])
    z_avg = stats.zscore(merged['shrunk_p_avg'])
    
    raw = 0.20 * z_sr + 0.05 * z_avg + 0.20 * z_delta + 0.15 * z_bdry + 0.15 * z_ext + 0.15 * z_cons + 0.10 * z_sr
    clutch = stats.norm.cdf(raw) * 100.0
    merged[f'rating_{comp_name}'] = (clutch * (0.80 + 0.20 * merged['confidence'])).round(2)
    merged[f'conf_{comp_name}'] = merged['confidence']
    merged[f'balls_{comp_name}'] = merged['p_balls']
    
    return merged

def evaluate_format_bowling(df_delivs, comp_name='ALL'):
    p_mask = df_delivs['bowling_pressure'] >= 50
    norm_mask = df_delivs['bowling_pressure'] < 50
    ext_mask = df_delivs['bowling_pressure'] >= 70
    
    p_grp = df_delivs[p_mask].groupby(['bowler_id', 'bowler_name']).agg(
        p_runs=('bowler_runs_conceded', 'sum'),
        p_balls=('is_legal_bowl', 'sum'),
        p_wkts=('is_bowler_wicket', 'sum'),
        p_dots=('is_bowler_dot', 'sum'),
        p_bdry=('is_bowler_boundary', 'sum'),
        p_matches=('match_id', 'nunique')
    ).reset_index()
    
    norm_grp = df_delivs[norm_mask].groupby(['bowler_id', 'bowler_name']).agg(
        norm_runs=('bowler_runs_conceded', 'sum'),
        norm_balls=('is_legal_bowl', 'sum'),
        norm_wkts=('is_bowler_wicket', 'sum')
    ).reset_index()
    
    ext_grp = df_delivs[ext_mask].groupby(['bowler_id', 'bowler_name']).agg(
        ext_runs=('bowler_runs_conceded', 'sum'),
        ext_balls=('is_legal_bowl', 'sum'),
        ext_wkts=('is_bowler_wicket', 'sum')
    ).reset_index()
    
    merged = p_grp.merge(norm_grp, on=['bowler_id', 'bowler_name'], how='left').fillna(0)
    merged = merged.merge(ext_grp, on=['bowler_id', 'bowler_name'], how='left').fillna(0)
    
    merged['p_overs'] = merged['p_balls'] / 6.0
    merged['norm_overs'] = merged['norm_balls'] / 6.0
    merged['ext_overs'] = merged['ext_balls'] / 6.0
    
    merged['p_econ'] = np.where(merged['p_overs'] > 0, merged['p_runs'] / merged['p_overs'], 12.0)
    merged['norm_econ'] = np.where(merged['norm_overs'] > 0, merged['norm_runs'] / merged['norm_overs'], 12.0)
    merged['ext_econ'] = np.where(merged['ext_overs'] > 0, merged['ext_runs'] / merged['ext_overs'], 12.0)
    
    merged['p_wpo'] = np.where(merged['p_overs'] > 0, merged['p_wkts'] / merged['p_overs'], 0.0)
    merged['norm_wpo'] = np.where(merged['norm_overs'] > 0, merged['norm_wkts'] / merged['norm_overs'], 0.0)
    
    # Robust baseline delta: bounded and conditioned on pressure economy being <= 10.0 RPO
    raw_delta_econ = np.clip(merged['norm_econ'] - merged['p_econ'], -3.0, 4.0)
    quality_mult_bowl = np.clip((10.5 - merged['p_econ']) / 2.5, 0.0, 1.0)
    merged['delta_econ'] = raw_delta_econ * quality_mult_bowl
    
    merged['p_dot_pct'] = np.where(merged['p_balls'] > 0, (merged['p_dots'] / merged['p_balls']) * 100.0, 0.0)
    merged['p_bdry_pct'] = np.where(merged['p_balls'] > 0, (merged['p_bdry'] / merged['p_balls']) * 100.0, 0.0)
    
    # Consistency
    match_bowl = df_delivs[p_mask].groupby(['bowler_id', 'match_id']).agg(
        r=('bowler_runs_conceded', 'sum'), b=('is_legal_bowl', 'sum')
    ).reset_index()
    match_bowl['econ'] = np.where(match_bowl['b'] > 0, (match_bowl['r'] / match_bowl['b']) * 6.0, 12.0)
    b_stats = match_bowl.groupby('bowler_id')['econ'].agg(['std', 'count']).reset_index()
    b_stats['consistency'] = np.clip(1.0 - (b_stats['std'].fillna(3.0) / 6.0), 0.1, 1.0)
    merged = merged.merge(b_stats[['bowler_id', 'consistency']], on='bowler_id', how='left').fillna({'consistency': 0.3})
    
    # Shrinkage
    mu_econ = (df_delivs[p_mask]['bowler_runs_conceded'].sum() / (df_delivs[p_mask]['is_legal_bowl'].sum() / 6.0))
    mu_wpo = (df_delivs[p_mask]['is_bowler_wicket'].sum() / (df_delivs[p_mask]['is_legal_bowl'].sum() / 6.0))
    K = 36.0
    
    merged['shrunk_p_econ'] = (merged['p_balls'] / (merged['p_balls'] + K)) * merged['p_econ'] + (K / (merged['p_balls'] + K)) * mu_econ
    merged['shrunk_p_wpo'] = (merged['p_balls'] / (merged['p_balls'] + K)) * merged['p_wpo'] + (K / (merged['p_balls'] + K)) * mu_wpo
    merged['confidence'] = 1.0 - np.exp(-merged['p_balls'] / 60.0)
    
    z_econ = -stats.zscore(merged['shrunk_p_econ'])
    z_wpo = stats.zscore(merged['shrunk_p_wpo'])
    z_delta_econ = stats.zscore(merged['delta_econ'])
    z_dot_bdry = stats.zscore(merged['p_dot_pct'] - merged['p_bdry_pct'])
    z_ext_econ = -stats.zscore(np.where(merged['ext_balls'] > 0, merged['ext_econ'], mu_econ))
    z_cons = stats.zscore(merged['consistency'])
    
    raw = 0.25 * z_econ + 0.20 * z_wpo + 0.15 * z_delta_econ + 0.15 * z_dot_bdry + 0.15 * z_ext_econ + 0.10 * z_cons
    clutch = stats.norm.cdf(raw) * 100.0
    merged[f'rating_{comp_name}'] = (clutch * (0.80 + 0.20 * merged['confidence'])).round(2)
    merged[f'conf_{comp_name}'] = merged['confidence']
    merged[f'balls_{comp_name}'] = merged['p_balls']
    
    return merged

print("Evaluating IPL and T20I Batting...")
bat_ipl = evaluate_format_batting(bbb_df[bbb_df['is_ipl']], comp_name='IPL')
bat_t20i = evaluate_format_batting(bbb_df[bbb_df['match_format'] == 'T20I'], comp_name='T20I')

# Combine Batting
bat_all_p = bbb_df[bbb_df['batting_pressure'] >= 50].groupby(['striker_id', 'striker_name']).agg(
    total_p_balls=('is_batter_ball', 'sum'),
    total_p_runs=('runs', 'sum'),
    total_p_outs=('is_batter_out', 'sum'),
    total_p_matches=('match_id', 'nunique')
).reset_index()

bat_comb = bat_all_p.merge(bat_ipl[['striker_id', 'rating_IPL', 'conf_IPL', 'balls_IPL', 'p_sr', 'ext_sr']], on='striker_id', how='left').fillna(0)
bat_comb = bat_comb.merge(bat_t20i[['striker_id', 'rating_T20I', 'conf_T20I', 'balls_T20I', 'p_sr', 'ext_sr']], on='striker_id', how='left', suffixes=('_ipl', '_t20i')).fillna(0)

# Compute Combined Rating (70% IPL / 30% T20I weighted by confidence)
def blend_rating(r_ipl, c_ipl, r_t20i, c_t20i):
    if c_ipl > 0 and c_t20i > 0:
        w_ipl = (0.70 * c_ipl) / (0.70 * c_ipl + 0.30 * c_t20i)
        w_t20i = (0.30 * c_t20i) / (0.70 * c_ipl + 0.30 * c_t20i)
        return w_ipl * r_ipl + w_t20i * r_t20i
    elif c_ipl > 0:
        return r_ipl
    elif c_t20i > 0:
        return r_t20i * 0.92
    else:
        return 0.0

bat_comb['final_clutch_rating'] = [blend_rating(r1, c1, r2, c2) for r1, c1, r2, c2 in zip(bat_comb['rating_IPL'], bat_comb['conf_IPL'], bat_comb['rating_T20I'], bat_comb['conf_T20I'])]
bat_comb['final_clutch_rating'] = bat_comb['final_clutch_rating'].round(2)

# Eligibility: Minimum 60 pressure balls total, min 10 matches
bat_comb['is_eligible'] = (bat_comb['total_p_balls'] >= 60) & (bat_comb['total_p_matches'] >= 8)

print("\n" + "="*70)
print("COMBINED TOP 10 BATTERS UNDER PRESSURE (70% IPL / 30% T20I)")
print("="*70)
top10_bat = bat_comb[bat_comb['is_eligible']].sort_values('final_clutch_rating', ascending=False).head(10).reset_index(drop=True)
top10_bat['Rank'] = range(1, 11)
print(top10_bat[['Rank', 'striker_name', 'striker_id', 'final_clutch_rating', 'rating_IPL', 'rating_T20I', 'total_p_balls', 'total_p_runs', 'total_p_matches']])

# Bowling Combine
print("\nEvaluating IPL and T20I Bowling...")
bowl_ipl = evaluate_format_bowling(bbb_df[bbb_df['is_ipl']], comp_name='IPL')
bowl_t20i = evaluate_format_bowling(bbb_df[bbb_df['match_format'] == 'T20I'], comp_name='T20I')

bowl_all_p = bbb_df[bbb_df['bowling_pressure'] >= 50].groupby(['bowler_id', 'bowler_name']).agg(
    total_p_balls=('is_legal_bowl', 'sum'),
    total_p_runs=('bowler_runs_conceded', 'sum'),
    total_p_wkts=('is_bowler_wicket', 'sum'),
    total_p_matches=('match_id', 'nunique')
).reset_index()

bowl_comb = bowl_all_p.merge(bowl_ipl[['bowler_id', 'rating_IPL', 'conf_IPL', 'balls_IPL', 'p_econ', 'p_wkts']], on='bowler_id', how='left').fillna(0)
bowl_comb = bowl_comb.merge(bowl_t20i[['bowler_id', 'rating_T20I', 'conf_T20I', 'balls_T20I', 'p_econ', 'p_wkts']], on='bowler_id', how='left', suffixes=('_ipl', '_t20i')).fillna(0)

bowl_comb['final_clutch_rating'] = [blend_rating(r1, c1, r2, c2) for r1, c1, r2, c2 in zip(bowl_comb['rating_IPL'], bowl_comb['conf_IPL'], bowl_comb['rating_T20I'], bowl_comb['conf_T20I'])]
bowl_comb['final_clutch_rating'] = bowl_comb['final_clutch_rating'].round(2)

# Eligibility: Minimum 90 pressure legal balls (15 pressure overs), min 10 matches
bowl_comb['is_eligible'] = (bowl_comb['total_p_balls'] >= 90) & (bowl_comb['total_p_matches'] >= 10)

print("\n" + "="*70)
print("COMBINED TOP 10 BOWLERS UNDER PRESSURE (70% IPL / 30% T20I)")
print("="*70)
top10_bowl = bowl_comb[bowl_comb['is_eligible']].sort_values('final_clutch_rating', ascending=False).head(10).reset_index(drop=True)
top10_bowl['Rank'] = range(1, 11)
print(top10_bowl[['Rank', 'bowler_name', 'bowler_id', 'final_clutch_rating', 'rating_IPL', 'rating_T20I', 'total_p_balls', 'total_p_wkts', 'total_p_matches']])
