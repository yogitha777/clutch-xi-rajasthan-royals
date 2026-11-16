import pandas as pd

bbb_df = pd.read_csv('Data Pack/ball_by_ball.csv')

# Check run outs: does dismissed_player_id distinguish striker vs non-striker?
runouts = bbb_df[bbb_df['dismissal_type'] == 'RunOut']
print(f"Total runouts: {len(runouts)}")
striker_out = (runouts['dismissed_player_id'] == runouts['striker_id']).sum()
non_striker_out = (runouts['dismissed_player_id'] == runouts['non_striker_id']).sum()
other_out = len(runouts) - (striker_out + non_striker_out)
print(f"Runouts striker dismissed: {striker_out}, non-striker dismissed: {non_striker_out}, other: {other_out}")

# Check dismissal types and whether dismissed_player_id is always present when is_wicket == True
wickets = bbb_df[bbb_df['is_wicket'] == True]
print(f"Total wickets: {len(wickets)}")
print(f"Null dismissed_player_id in wickets: {wickets['dismissed_player_id'].isna().sum()}")
print("Dismissal type value counts:")
print(wickets['dismissal_type'].value_counts())

# Check bowler wickets vs non-bowler wickets
bowler_wickets = wickets[wickets['dismissal_type'].isin(['Caught', 'Bowled', 'LBW', 'Stump', 'Hit Wicket'])]
print(f"Bowler credited wickets: {len(bowler_wickets)}")
print(f"Non-bowler wickets: {len(wickets) - len(bowler_wickets)}")
