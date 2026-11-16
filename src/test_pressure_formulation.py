import pandas as pd
import numpy as np

print("Loading ball_by_ball and matches data...")
matches_df = pd.read_csv('Data Pack/matches.csv')
bbb_df = pd.read_csv('Data Pack/ball_by_ball.csv')

# Sort deliveries chronologically within each match & innings
bbb_df = bbb_df.sort_values(['match_id', 'innings', 'overid', 'over_ball_num']).reset_index(drop=True)

# Determine legal ball flag
# In T20 cricket: wides and no-balls (Overstep, other) are not legal balls
bbb_df['is_legal_ball'] = ~bbb_df['extras_type'].isin(['wide', 'Overstep', 'other'])

# Total runs on delivery
bbb_df['delivery_runs'] = bbb_df['runs'] + bbb_df['extras1_runs'] + bbb_df['extras_2_runs']

# Bowler runs conceded on delivery: runs off bat + wides + no-balls
# legbyes, byes, penalty do NOT count against bowler
bbb_df['bowler_extras'] = 0
bbb_df.loc[bbb_df['extras_type'] == 'wide', 'bowler_extras'] = bbb_df['extras1_runs'] + bbb_df['extras_2_runs']
bbb_df.loc[bbb_df['extras_type'].isin(['Overstep', 'other']), 'bowler_extras'] = bbb_df['extras1_runs']
bbb_df['bowler_runs_conceded'] = bbb_df['runs'] + bbb_df['bowler_extras']

# Bowler wicket flag: dismissal_type in ['Caught', 'Bowled', 'LBW', 'Stump', 'Hit Wicket']
bbb_df['is_bowler_wicket'] = bbb_df['is_wicket'] & bbb_df['dismissal_type'].isin(['Caught', 'Bowled', 'LBW', 'Stump', 'Hit Wicket'])

print("Calculating pre-delivery state variables...")

# Calculate state BEFORE each delivery:
# Group by match_id, innings
bbb_df['runs_before'] = bbb_df.groupby(['match_id', 'innings'])['delivery_runs'].cumsum() - bbb_df['delivery_runs']
bbb_df['wickets_before'] = bbb_df.groupby(['match_id', 'innings'])['is_wicket'].cumsum() - bbb_df['is_wicket']
bbb_df['legal_balls_before'] = bbb_df.groupby(['match_id', 'innings'])['is_legal_ball'].cumsum() - bbb_df['is_legal_ball']

# Get match target
inn1_runs = bbb_df[bbb_df['innings'] == 1].groupby('match_id')['delivery_runs'].sum().rename('inn1_total')
matches_targets = matches_df[['match_id', 'first_inn_revised_overs', 'second_inn_revised_overs', 'revised_target']].copy()
matches_targets = matches_targets.merge(inn1_runs, on='match_id', how='left')

# Target for 2nd innings
matches_targets['target'] = matches_targets['revised_target']
matches_targets.loc[matches_targets['target'].isna() & matches_targets['inn1_total'].notna(), 'target'] = matches_targets['inn1_total'] + 1

# Merge back to bbb_df
bbb_df = bbb_df.merge(matches_targets[['match_id', 'target', 'first_inn_revised_overs', 'second_inn_revised_overs']], on='match_id', how='left')

# Scheduled balls per innings (default 120, or revised_overs * 6)
bbb_df['scheduled_balls_inn1'] = 120.0
mask1 = bbb_df['first_inn_revised_overs'].notna()
bbb_df.loc[mask1, 'scheduled_balls_inn1'] = bbb_df.loc[mask1, 'first_inn_revised_overs'] * 6.0

bbb_df['scheduled_balls_inn2'] = 120.0
mask2 = bbb_df['second_inn_revised_overs'].notna()
bbb_df.loc[mask2, 'scheduled_balls_inn2'] = bbb_df.loc[mask2, 'second_inn_revised_overs'] * 6.0

bbb_df['scheduled_balls'] = np.where(bbb_df['innings'] == 1, bbb_df['scheduled_balls_inn1'], bbb_df['scheduled_balls_inn2'])
bbb_df['balls_remaining'] = np.maximum(0, bbb_df['scheduled_balls'] - bbb_df['legal_balls_before'])
bbb_df['wickets_in_hand'] = np.maximum(0, 10 - bbb_df['wickets_before'])

# Innings 2: runs needed and RRR
bbb_df['runs_needed'] = np.where(bbb_df['innings'] == 2, np.maximum(0, bbb_df['target'] - bbb_df['runs_before']), np.nan)
bbb_df['rrr'] = np.where(
    (bbb_df['innings'] == 2) & (bbb_df['balls_remaining'] > 0),
    (bbb_df['runs_needed'] / bbb_df['balls_remaining']) * 6.0,
    np.nan
)
bbb_df['crr'] = np.where(
    bbb_df['legal_balls_before'] > 0,
    (bbb_df['runs_before'] / bbb_df['legal_balls_before']) * 6.0,
    8.0
)

print("\nState calculation complete. Sample 2nd innings state:")
sample_chase = bbb_df[bbb_df['innings'] == 2][['match_id', 'overid', 'over_ball_num', 'runs_before', 'wickets_in_hand', 'balls_remaining', 'target', 'runs_needed', 'rrr']].head(10)
print(sample_chase)
