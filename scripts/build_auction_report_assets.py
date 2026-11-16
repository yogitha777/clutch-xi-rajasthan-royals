import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

os.makedirs('final_submission/figures', exist_ok=True)
os.makedirs('output/figures', exist_ok=True)

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#CBD5E1'
plt.rcParams['axes.linewidth'] = 0.8

# 1. Top 10 Batters Chart
tb = pd.read_csv('final_submission/Top_10_Batters.csv')
fig, ax = plt.subplots(figsize=(10, 4.5), dpi=300)
fig.patch.set_facecolor('#FFFFFF')
ax.set_facecolor('#F8FAFC')

y_pos = np.arange(len(tb))
height = 0.36

rects1 = ax.barh(y_pos - height/2, tb['pressure_sr'], height, label='Pressure SR (P >= 50)', color='#0B132B', edgecolor='none')
rects2 = ax.barh(y_pos + height/2, tb['extreme_sr'], height, label='Extreme Pressure SR (P >= 70)', color='#E60067', edgecolor='none')

ax.set_yticks(y_pos)
ax.set_yticklabels([f"#{int(r.Rank)} {r.Player_Name} ({r.clutch_rating:.1f})" for _, r in tb.iterrows()], fontsize=8.5, fontweight='bold', color='#0F172A')
ax.invert_yaxis()
ax.set_xlabel('Strike Rate', fontsize=9.5, fontweight='bold', color='#0F172A')
ax.set_title('Top 10 Batters Under Pressure: Strike Rate Acceleration in Crisis Moments (P >= 70)', fontsize=11, fontweight='bold', color='#0B132B', pad=10)
ax.axvline(133.87, color='#64748B', linestyle='--', linewidth=1, label='League Benchmark SR (133.9)')
ax.legend(loc='lower right', frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1', fontsize=8)
ax.grid(axis='x', linestyle=':', alpha=0.6, color='#94A3B8')

plt.tight_layout()
fig.savefig('final_submission/figures/fig_top10_batters_chart.png')
fig.savefig('output/figures/fig_top10_batters_chart.png')
plt.close()
print("1. Batters chart updated with P >= 70.")

# 2. Top 10 Bowlers Chart
tb_bowl = pd.read_csv('final_submission/Top_10_Bowlers.csv')
fig, ax = plt.subplots(figsize=(10, 4.5), dpi=300)
fig.patch.set_facecolor('#FFFFFF')
ax.set_facecolor('#F8FAFC')

y_pos = np.arange(len(tb_bowl))
height = 0.36

rects1 = ax.barh(y_pos - height/2, tb_bowl['pressure_econ'], height, label='Pressure Economy (P >= 50)', color='#0B132B', edgecolor='none')
rects2 = ax.barh(y_pos + height/2, tb_bowl['extreme_econ'], height, label='Extreme Pressure Economy (P >= 70)', color='#E60067', edgecolor='none')

ax.set_yticks(y_pos)
ax.set_yticklabels([f"#{int(r.Rank)} {r.Player_Name} ({r.clutch_rating:.1f})" for _, r in tb_bowl.iterrows()], fontsize=8.5, fontweight='bold', color='#0F172A')
ax.invert_yaxis()
ax.set_xlabel('Economy Rate (Runs / Over) — Lower is Better', fontsize=9.5, fontweight='bold', color='#0F172A')
ax.set_title('Top 10 Bowlers Under Pressure: Economy Rate Suppression in High-Stress Overs (P >= 70)', fontsize=11, fontweight='bold', color='#0B132B', pad=10)
ax.axvline(9.06, color='#64748B', linestyle='--', linewidth=1, label='League Benchmark Econ (9.06)')
ax.legend(loc='lower right', frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1', fontsize=8)
ax.grid(axis='x', linestyle=':', alpha=0.6, color='#94A3B8')

plt.tight_layout()
fig.savefig('final_submission/figures/fig_top10_bowlers_chart.png')
fig.savefig('output/figures/fig_top10_bowlers_chart.png')
plt.close()
print("2. Bowlers chart updated with P >= 70.")

# 3. Problem Gap Chart: Career vs Pressure vs Extreme SR
fig, ax = plt.subplots(figsize=(9, 4.0), dpi=300)
fig.patch.set_facecolor('#FFFFFF')
ax.set_facecolor('#F8FAFC')

sample_players = ['Jos Buttler', 'Ashutosh Sharma', 'Tim David', 'N. Tilak Varma', 'Glenn Maxwell']
career_srs = [155.39, 166.28, 177.65, 142.98, 160.96]
pressure_srs = [181.35, 177.31, 186.55, 155.28, 175.92]
extreme_srs = [237.93, 192.22, 195.39, 188.89, 223.53]

x = np.arange(len(sample_players))
width = 0.25

ax.bar(x - width, career_srs, width, label='Career / Low Pressure SR', color='#94A3B8')
ax.bar(x, pressure_srs, width, label='High Pressure SR (50 <= P < 70)', color='#0B132B')
ax.bar(x + width, extreme_srs, width, label='Extreme Pressure SR (P >= 70)', color='#E60067')

ax.set_ylabel('Strike Rate', fontsize=9.5, fontweight='bold', color='#0F172A')
ax.set_title('The Performance Divergence: Career Metrics vs Crisis-Moment Execution', fontsize=11, fontweight='bold', color='#0B132B', pad=10)
ax.set_xticks(x)
ax.set_xticklabels(sample_players, fontsize=9, fontweight='bold', color='#0F172A')
ax.legend(loc='upper left', frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1', fontsize=8)
ax.grid(axis='y', linestyle=':', alpha=0.6, color='#94A3B8')

plt.tight_layout()
fig.savefig('final_submission/figures/fig_problem_gap.png')
fig.savefig('output/figures/fig_problem_gap.png')
plt.close()
print("3. Problem gap chart updated.")

# 4. Bowler Quadrants: Economy vs WPO
fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=300)
fig.patch.set_facecolor('#FFFFFF')
ax.set_facecolor('#F8FAFC')

for _, r in tb_bowl.iterrows():
    ax.scatter(r['pressure_econ'], r['pressure_wpo'], color='#E60067' if r['Rank'] <= 3 else '#0B132B', s=70, zorder=5)
    ax.annotate(r['Player_Name'].split()[-1], (r['pressure_econ'] + 0.08, r['pressure_wpo'] + 0.005), fontsize=8, fontweight='bold', color='#0F172A')

ax.axvline(7.5, color='#CBD5E1', linestyle='--', linewidth=1)
ax.axhline(0.35, color='#CBD5E1', linestyle='--', linewidth=1)

ax.text(5.2, 0.58, 'QUADRANT I:\nElite Strike Containment\n(Low Econ, High Wkts)', fontsize=8, color='#059669', fontweight='bold', bbox=dict(boxstyle='round,pad=0.3', facecolor='#ECFDF5', edgecolor='#10B981', alpha=0.8))
ax.text(8.0, 0.58, 'QUADRANT II:\nStrike Enforcers\n(Higher Econ, High Wkts)', fontsize=8, color='#D97706', fontweight='bold', bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFFBEB', edgecolor='#F59E0B', alpha=0.8))
ax.text(5.2, 0.22, 'QUADRANT III:\nChoke Spinners\n(Ultra Low Econ)', fontsize=8, color='#2563EB', fontweight='bold', bbox=dict(boxstyle='round,pad=0.3', facecolor='#EFF6FF', edgecolor='#3B82F6', alpha=0.8))

ax.set_xlabel('Pressure Economy Rate (Runs / Over)', fontsize=9.5, fontweight='bold', color='#0F172A')
ax.set_ylabel('Pressure Wickets Per Over (WPO)', fontsize=9.5, fontweight='bold', color='#0F172A')
ax.set_title('Tactical Bowling Roles Under Pressure: Economy vs Strike Rate Quadrants', fontsize=11, fontweight='bold', color='#0B132B', pad=10)
ax.grid(True, linestyle=':', alpha=0.5, color='#94A3B8')

plt.tight_layout()
fig.savefig('final_submission/figures/fig_bowler_quadrants.png')
fig.savefig('output/figures/fig_bowler_quadrants.png')
plt.close()
print("4. Bowler quadrants chart updated.")
