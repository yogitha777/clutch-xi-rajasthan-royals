import pandas as pd
import numpy as np

# Load bbb with metadata
from model_pressure import bbb_df, matches_df

comp_df = pd.read_csv('Data Pack/competitions.csv')
matches_meta = matches_df[['match_id', 'comp_id']].merge(comp_df[['comp_id', 'comp_name', 'match_format', 'season']], on='comp_id', how='left')
bbb_df = bbb_df.merge(matches_meta[['match_id', 'comp_name', 'match_format', 'season']], on='match_id', how='left')
bbb_df['is_ipl'] = bbb_df['comp_name'].str.contains('IPL', na=False)

print("--- Competition Scoring Environments under Pressure (Pressure >= 50) ---")
p_delivs = bbb_df[bbb_df['bowling_pressure'] >= 50]

for grp_name, sub in [('IPL (2022-2026)', p_delivs[p_delivs['is_ipl']]),
                      ('T20 Internationals', p_delivs[p_delivs['match_format'] == 'T20I']),
                      ('All Pressure Deliveries', p_delivs)]:
    legal_b = sub[sub['is_legal_ball']]
    runs = sub['bowler_runs_conceded'].sum()
    wkts = sub['is_bowler_wicket'].sum()
    overs = len(legal_b) / 6.0
    econ = runs / overs
    sr = len(legal_b) / max(1, wkts)
    print(f"{grp_name:25s} | Overs: {overs:7.1f} | Econ: {econ:5.2f} | Bowling SR: {sr:5.2f} | Wkts/Over: {wkts/overs:5.3f}")

# Check Batting Scoring Environments under Pressure (Batting Pressure >= 50)
bat_p_delivs = bbb_df[bbb_df['batting_pressure'] >= 50]
print("\n--- Batting Environments under Pressure (Batting Pressure >= 50) ---")
for grp_name, sub in [('IPL (2022-2026)', bat_p_delivs[bat_p_delivs['is_ipl']]),
                      ('T20 Internationals', bat_p_delivs[bat_p_delivs['match_format'] == 'T20I']),
                      ('All Pressure Deliveries', bat_p_delivs)]:
    balls = sub[sub['extras_type'] != 'wide']
    runs = sub['runs'].sum()
    outs = (sub['is_wicket'] & (sub['dismissed_player_id'] == sub['striker_id'])).sum()
    bat_sr = (runs / len(balls)) * 100.0
    bat_avg = runs / max(1, outs)
    print(f"{grp_name:25s} | Balls: {len(balls):6d} | Strike Rate: {bat_sr:6.2f} | Batting Avg: {bat_avg:5.2f}")

