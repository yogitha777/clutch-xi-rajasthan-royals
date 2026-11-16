import os
import pandas as pd
import numpy as np

print("Generating Data Quality Report...")

# Load all files
comp_df = pd.read_csv('Data Pack/competitions.csv')
teams_df = pd.read_csv('Data Pack/teams.csv')
matches_df = pd.read_csv('Data Pack/matches.csv')
p11_df = pd.read_csv('Data Pack/playing_eleven.csv')
mapping_df = pd.read_csv('Data Pack/competition_team_player_mapping.csv')
bbb_df = pd.read_csv('Data Pack/ball_by_ball.csv')

report_rows = []

# Table stats
tables = {
    'competitions': comp_df,
    'teams': teams_df,
    'matches': matches_df,
    'playing_eleven': p11_df,
    'competition_team_player_mapping': mapping_df,
    'ball_by_ball': bbb_df
}

for name, df in tables.items():
    null_cols = df.isnull().sum()
    null_cols_str = "; ".join([f"{c}:{v}" for c, v in null_cols.items() if v > 0])
    dup_rows = df.duplicated().sum()
    report_rows.append({
        'Table': name,
        'Total_Rows': len(df),
        'Total_Columns': len(df.columns),
        'Duplicate_Rows': dup_rows,
        'Columns_With_Nulls': null_cols_str if null_cols_str else 'None',
        'Key_Metrics': f"Unique Primary Keys/IDs: {df.iloc[:, 0].nunique()}"
    })

quality_summary_df = pd.DataFrame(report_rows)
quality_summary_df.to_csv('output/Data_Quality_Report.csv', index=False)
print("Data Quality Report saved to output/Data_Quality_Report.csv")

# Print detailed findings
print("\n" + "="*70)
print("PHASE 1 DATA QUALITY AUDIT FINDINGS")
print("="*70)
for idx, r in quality_summary_df.iterrows():
    print(f"\nTABLE: {r['Table']}")
    print(f"  Rows: {r['Total_Rows']:,} | Columns: {r['Total_Columns']} | Duplicates: {r['Duplicate_Rows']}")
    print(f"  Nulls: {r['Columns_With_Nulls']}")
