import sys
sys.path.append('src')
from model_pressure import bbb_df

# Batters pressure balls faced (non-wides)
bf_pressure = bbb_df[(bbb_df['batting_pressure'] >= 50) & (bbb_df['extras_type'] != 'wide')].groupby(['striker_id', 'striker_name']).size().reset_index(name='pressure_bf')
print("Top 15 batters by pressure balls faced:")
print(bf_pressure.sort_values('pressure_bf', ascending=False).head(15))
print(f"Batters with >= 40 pressure balls: {(bf_pressure['pressure_bf'] >= 40).sum()}")
print(f"Batters with >= 50 pressure balls: {(bf_pressure['pressure_bf'] >= 50).sum()}")
print(f"Batters with >= 60 pressure balls: {(bf_pressure['pressure_bf'] >= 60).sum()}")
print(f"Batters with >= 80 pressure balls: {(bf_pressure['pressure_bf'] >= 80).sum()}")
print(f"Batters with >= 100 pressure balls: {(bf_pressure['pressure_bf'] >= 100).sum()}")

# Bowlers pressure balls bowled (legal balls)
bb_pressure = bbb_df[(bbb_df['bowling_pressure'] >= 50) & (bbb_df['is_legal_ball'])].groupby(['bowler_id', 'bowler_name']).size().reset_index(name='pressure_bb')
print("\nTop 15 bowlers by pressure legal balls bowled:")
print(bb_pressure.sort_values('pressure_bb', ascending=False).head(15))
print(f"Bowlers with >= 40 pressure legal balls: {(bb_pressure['pressure_bb'] >= 40).sum()}")
print(f"Bowlers with >= 60 pressure legal balls: {(bb_pressure['pressure_bb'] >= 60).sum()}")
print(f"Bowlers with >= 100 pressure legal balls: {(bb_pressure['pressure_bb'] >= 100).sum()}")
print(f"Bowlers with >= 150 pressure legal balls: {(bb_pressure['pressure_bb'] >= 150).sum()}")
