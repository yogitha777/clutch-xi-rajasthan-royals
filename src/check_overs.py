import pandas as pd

bbb_df = pd.read_csv('Data Pack/ball_by_ball.csv')

for et in ['wide', 'Overstep', 'legbyes', 'byes', 'other', 'Penalty']:
    sub = bbb_df[bbb_df['extras_type'] == et]
    print(f"Extras: {et:10s} | Count: {len(sub):6d} | extras1 mean: {sub['extras1_runs'].mean():.2f} | extras2 mean: {sub['extras_2_runs'].mean():.2f} | runs mean: {sub['runs'].mean():.2f}")

# Check over containing row 532
row532 = bbb_df.loc[532]
m_id, inn, ov = row532['match_id'], row532['innings'], row532['overid']
print(f"\nFull over for match {m_id}, inn {inn}, over {ov}:")
ov_df = bbb_df[(bbb_df['match_id'] == m_id) & (bbb_df['innings'] == inn) & (bbb_df['overid'] == ov)].sort_values(['over_ball_num'])
print(ov_df[['over_ball_num', 'innings_ball_num', 'striker_name', 'bowler_name', 'runs', 'extras_type', 'extras1_runs', 'extras_2_runs', 'is_wicket']])
print(f"Total deliveries in this over: {len(ov_df)}")
