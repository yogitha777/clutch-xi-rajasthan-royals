import pandas as pd
import numpy as np

# Load bbb with calculated pressure from model_pressure
from model_pressure import bbb_df, matches_df

print("="*70)
print("WORKED EXAMPLES: VALIDATING PRESSURE CLASSIFICATION")
print("="*70)

# Example 1: IPL 2023 Final (Chennai Super Kings vs Gujarat Titans - DLS thriller) or a close chase
close_matches = matches_df[matches_df['result'].str.contains('Won by 1 wicket|Won by 2 wickets|Won by 1 Run|Won by 2 Runs|Super Over', case=False, na=False)]
print(f"Close matches count: {len(close_matches)}")
sample_close_id = close_matches.iloc[0]['match_id']
m_info = close_matches.iloc[0]
print(f"\nExample 1: Match {sample_close_id} | {m_info['home_team']} vs {m_info['away_team']} | Result: {m_info['result']}")

sample_delivs = bbb_df[(bbb_df['match_id'] == sample_close_id) & (bbb_df['innings'] == 2) & (bbb_df['overid'] >= 18)]
print(sample_delivs[['overid', 'over_ball_num', 'striker_name', 'bowler_name', 'runs_before', 'wickets_in_hand', 'balls_remaining', 'runs_needed', 'rrr', 'batting_pressure', 'bat_tier', 'bowling_pressure', 'bowl_tier']].head(10))

# Example 2: First Innings Collapse
# Find a match where wickets >= 3 in first 5 overs (powerplay)
collapse = bbb_df[(bbb_df['innings'] == 1) & (bbb_df['overid'] <= 5) & (bbb_df['wickets_before'] >= 3)]
if len(collapse) > 0:
    col_mid = collapse.iloc[0]['match_id']
    m_col = matches_df[matches_df['match_id'] == col_mid].iloc[0]
    print(f"\nExample 2: 1st Innings Collapse | Match {col_mid} | {m_col['home_team']} vs {m_col['away_team']}")
    col_delivs = bbb_df[(bbb_df['match_id'] == col_mid) & (bbb_df['innings'] == 1) & (bbb_df['overid'] <= 6)]
    print(col_delivs[['overid', 'over_ball_num', 'striker_name', 'bowler_name', 'runs_before', 'wickets_before', 'crr', 'batting_pressure', 'bat_tier']].tail(8))

# Example 3: Low Pressure Cruise (Blowout / Easy Chase)
easy = bbb_df[(bbb_df['innings'] == 2) & (bbb_df['rrr'] < 5.0) & (bbb_df['wickets_in_hand'] >= 8) & (bbb_df['overid'] >= 10)]
if len(easy) > 0:
    easy_mid = easy.iloc[0]['match_id']
    m_easy = matches_df[matches_df['match_id'] == easy_mid].iloc[0]
    print(f"\nExample 3: Low Pressure Cruise | Match {easy_mid} | {m_easy['home_team']} vs {m_easy['away_team']}")
    easy_delivs = bbb_df[(bbb_df['match_id'] == easy_mid) & (bbb_df['innings'] == 2) & (bbb_df['overid'] >= 10)]
    print(easy_delivs[['overid', 'over_ball_num', 'striker_name', 'bowler_name', 'runs_before', 'wickets_in_hand', 'runs_needed', 'rrr', 'batting_pressure', 'bat_tier']].head(8))
