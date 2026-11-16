import pandas as pd
import numpy as np

matches_df = pd.read_csv('Data Pack/matches.csv')
bbb_df = pd.read_csv('Data Pack/ball_by_ball.csv')

# Compute total innings runs per match & innings
# Total runs on a delivery = runs + extras1_runs + extras_2_runs
bbb_df['total_delivery_runs'] = bbb_df['runs'] + bbb_df['extras1_runs'] + bbb_df['extras_2_runs']

inn_totals = bbb_df.groupby(['match_id', 'innings'])['total_delivery_runs'].sum().unstack()
print("Innings totals sample (first 10 matches):")
print(inn_totals.head(10))

# Merge with matches
matches_merged = matches_df.merge(inn_totals, on='match_id', how='inner')
print(f"Matches with ball by ball data: {len(matches_merged)}")

# Check revised target vs first innings total
revised = matches_merged[matches_merged['revised_target'].notna()]
print(f"Matches with revised target: {len(revised)}")
print(revised[['match_id', 1, 2, 'first_inn_revised_overs', 'second_inn_revised_overs', 'revised_target', 'result']].head(10))

# Check normal matches: target = inn1_total + 1
normal = matches_merged[matches_merged['revised_target'].isna() & matches_merged[1].notna() & matches_merged[2].notna()]
print(f"Normal 2-innings matches: {len(normal)}")

# Check if target is achieved in 2nd innings
normal['target'] = normal[1] + 1
normal['diff'] = normal[2] - normal['target']
print("Normal matches summary:")
print(f"Wins chasing (diff >= 0): {(normal['diff'] >= 0).sum()}, Defended (diff < 0): {(normal['diff'] < 0).sum()}")

