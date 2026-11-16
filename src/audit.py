import os
import pandas as pd
import numpy as np

print("=" * 60)
print("PHASE 1: COMPREHENSIVE DATA AUDIT & SCHEMA INSPECTION")
print("=" * 60)

# 1. Competitions
comp_df = pd.read_csv('Data Pack/competitions.csv')
print("\n--- 1. Competitions ---")
print(f"Total rows: {len(comp_df)}")
print(comp_df.info())
print("Formats:", comp_df['match_format'].value_counts().to_dict())
print("Seasons:", comp_df['season'].value_counts().to_dict())
ipl_comps = comp_df[comp_df['comp_name'].str.contains('Indian Premier League|IPL', case=False, na=False)]
print(f"IPL Competitions ({len(ipl_comps)}):")
print(ipl_comps[['comp_id', 'comp_name', 'season']])

# 2. Teams
teams_df = pd.read_csv('Data Pack/teams.csv')
print("\n--- 2. Teams ---")
print(f"Total rows: {len(teams_df)}, Unique teams: {teams_df['team_id'].nunique()}, Unique comp_ids: {teams_df['comp_id'].nunique()}")

# 3. Matches
matches_df = pd.read_csv('Data Pack/matches.csv')
print("\n--- 3. Matches ---")
print(f"Total matches: {len(matches_df)}")
print(f"Nulls in matches:\n{matches_df.isnull().sum()[matches_df.isnull().sum() > 0]}")
print(f"Unique competitions in matches: {matches_df['comp_id'].nunique()}")
print(f"Result value counts sample (top 5):\n{matches_df['result'].value_counts().head(5)}")
no_results = matches_df[matches_df['win_team_id'].isna()]
print(f"Matches with no winner / tie / abandoned: {len(no_results)}")

# 4. Ball by Ball
print("\n--- 4. Ball by Ball ---")
bbb_df = pd.read_csv('Data Pack/ball_by_ball.csv')
print(f"Total rows in ball_by_ball: {len(bbb_df):,}")
print("Columns:", bbb_df.columns.tolist())
print(f"Unique match_ids in bbb: {bbb_df['match_id'].nunique()}")
print(f"Innings distribution:\n{bbb_df['innings'].value_counts().sort_index()}")

# Check overid and over_ball_num
print(f"Overid range: min={bbb_df['overid'].min()}, max={bbb_df['overid'].max()}")
print(f"Sample over_ball_num range: min={bbb_df['over_ball_num'].min()}, max={bbb_df['over_ball_num'].max()}")
print(f"Sample innings_ball_num range: min={bbb_df['innings_ball_num'].min()}, max={bbb_df['innings_ball_num'].max()}")

# Extras inspection
print("\n--- 5. Extras Analysis ---")
print("Unique extras_type:", bbb_df['extras_type'].value_counts(dropna=False).to_dict())
print("extras1_runs value counts:\n", bbb_df['extras1_runs'].value_counts().to_dict())
print("extras_2_runs value counts:\n", bbb_df['extras_2_runs'].value_counts().to_dict())

# What is extras1_runs vs extras_2_runs vs runs?
print("\nCross-tab of extras_type with runs and extras1_runs:")
sample_extras = bbb_df[bbb_df['extras_type'].notna()][['extras_type', 'runs', 'extras1_runs', 'extras_2_runs', 'is_four', 'is_six']].drop_duplicates()
print(sample_extras.head(20))

# Dismissal analysis
print("\n--- 6. Dismissal Analysis ---")
print("Unique dismissal_type:", bbb_df['dismissal_type'].value_counts(dropna=False).to_dict())
print("is_wicket value counts:", bbb_df['is_wicket'].value_counts().to_dict())

# Cross-tab dismissal_type vs is_wicket
print("Dismissal types when is_wicket is True:")
print(bbb_df[bbb_df['is_wicket'] == True]['dismissal_type'].value_counts(dropna=False))

# Unique players
print("\n--- 7. Players Analysis ---")
unique_strikers = bbb_df['striker_id'].nunique()
unique_bowlers = bbb_df['bowler_id'].nunique()
all_bbb_players = set(bbb_df['striker_id']).union(set(bbb_df['non_striker_id'])).union(set(bbb_df['bowler_id']))
print(f"Unique strikers: {unique_strikers}, Unique bowlers: {unique_bowlers}, Total unique bbb players: {len(all_bbb_players)}")

mapping_df = pd.read_csv('Data Pack/competition_team_player_mapping.csv')
print(f"Total mappings: {len(mapping_df)}, Unique mapped players: {mapping_df['player_id'].nunique()}")

# Check overlap of bbb players in mapping
unmapped = all_bbb_players - set(mapping_df['player_id'])
print(f"BBB players missing from mapping: {len(unmapped)}")

p11_df = pd.read_csv('Data Pack/playing_eleven.csv')
print(f"Total playing_eleven rows: {len(p11_df)}, Unique matches: {p11_df['match_id'].nunique()}, Unique players: {p11_df['player_id'].nunique()}")

print("\nAUDIT SCRIPT COMPLETE.")
