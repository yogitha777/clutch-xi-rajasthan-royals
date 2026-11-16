import os
import pandas as pd
import numpy as np

# Competitions inspection
comp_df = pd.read_csv('Data Pack/competitions.csv')
print("All T20 competitions:")
print(comp_df[comp_df['match_format'] == 'T20'])

# Check matches and revised targets
matches_df = pd.read_csv('Data Pack/matches.csv')
print("\nMatches summary:")
print(f"Total matches: {len(matches_df)}")
print(f"revised_target not null count: {matches_df['revised_target'].notna().sum()}")
print("Sample revised targets:")
print(matches_df[matches_df['revised_target'].notna()][['match_id', 'first_inn_revised_overs', 'second_inn_revised_overs', 'revised_target', 'result']].head(10))

# Ball by ball delivery inspection
bbb_df = pd.read_csv('Data Pack/ball_by_ball.csv')

# Let's inspect a complete match innings 1 and 2 to see the exact scoring progression
sample_match_id = 13511
m1 = bbb_df[bbb_df['match_id'] == sample_match_id].sort_values(['innings', 'overid', 'over_ball_num'])
print(f"\nMatch {sample_match_id} delivery count: {len(m1)}")
print("Innings 1 summary:")
inn1 = m1[m1['innings'] == 1]
print(f"Balls: {len(inn1)}, Total batter runs: {inn1['runs'].sum()}, Total extras1: {inn1['extras1_runs'].sum()}, Total extras2: {inn1['extras_2_runs'].sum()}")
print(f"Total innings 1 runs = {inn1['runs'].sum() + inn1['extras1_runs'].sum() + inn1['extras_2_runs'].sum()}")
print(f"Wickets in inn 1: {inn1['is_wicket'].sum()}")

print("Innings 2 summary:")
inn2 = m1[m1['innings'] == 2]
print(f"Balls: {len(inn2)}, Total batter runs: {inn2['runs'].sum()}, Total extras1: {inn2['extras1_runs'].sum()}, Total extras2: {inn2['extras_2_runs'].sum()}")
print(f"Total innings 2 runs = {inn2['runs'].sum() + inn2['extras1_runs'].sum() + inn2['extras_2_runs'].sum()}")
print(f"Wickets in inn 2: {inn2['is_wicket'].sum()}")

# Let's check matches.csv result for match 13511
print("Result in matches.csv:", matches_df[matches_df['match_id'] == sample_match_id][['home_team', 'away_team', 'win_team_id', 'result']].to_dict(orient='records'))

# Check what constitutes legal deliveries vs non-legal deliveries
print("\nExtras types breakdown:")
print(bbb_df['extras_type'].value_counts(dropna=False))

# For each extras_type, does it count as legal ball?
# In cricket:
# - wide: not legal delivery (over_ball_num does not advance legal balls count)
# - Overstep: no-ball, not legal delivery
# - legbyes, byes, penalty, other: legal ball (unless wide/no ball!)
# Let's verify whether 'other' or 'Penalty' are no-balls/wides or legal balls
print("\n'other' extras_type details:")
print(bbb_df[bbb_df['extras_type'] == 'other'][['runs', 'extras1_runs', 'extras_2_runs', 'stroke', 'delivery_style']].head(10))

print("\n'Penalty' extras_type details:")
print(bbb_df[bbb_df['extras_type'] == 'Penalty'][['runs', 'extras1_runs', 'extras_2_runs', 'stroke', 'delivery_style']])

# Check bowlers: what extras count against bowler?
# Wides and Oversteps (no-balls) count against bowler.
# Byes and legbyes do NOT count against bowler.
# What about 'other'? Let's check if 'other' has extras1_runs or extras_2_runs and how it is described.

