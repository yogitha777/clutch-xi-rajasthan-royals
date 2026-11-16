import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

print("=" * 70)
print("GENERATING AUDITED HIGH-RESOLUTION PUBLICATION CHARTS")
print("=" * 70)

from model_pressure import bbb_df

os.makedirs('output/figures', exist_ok=True)

# Set global style
plt.style.use('dark_background')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']

NAVY = '#0F172A'
DARK_CARD = '#1E293B'
PINK = '#E60067'
GOLD = '#F59E0B'
CYAN = '#38BDF8'
WHITE = '#F8FAFC'
GRAY = '#94A3B8'

# -------------------------------------------------------------
# CHART 1: Real Empirical Pressure Score Distributions
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 3.5), dpi=300)
fig.patch.set_facecolor(NAVY)
ax.set_facecolor(DARK_CARD)

bat_press = bbb_df['batting_pressure'].values
bowl_press = bbb_df['bowling_pressure'].values

bat_mean, bat_std = bat_press.mean(), bat_press.std()
bowl_mean, bowl_std = bowl_press.mean(), bowl_press.std()

ax.hist(bat_press, bins=50, density=True, alpha=0.65, color=PINK, 
        label=f'Batting Pressure (Mean {bat_mean:.1f}, Std {bat_std:.1f})')
ax.hist(bowl_press, bins=50, density=True, alpha=0.55, color=CYAN, 
        label=f'Bowling Pressure (Mean {bowl_mean:.1f}, Std {bowl_std:.1f})')

ax.axvline(30, color='#64748B', linestyle='--', linewidth=1, label='Tier Cutoffs (30, 50, 70)')
ax.axvline(50, color=GOLD, linestyle='--', linewidth=1.2)
ax.axvline(70, color=PINK, linestyle='--', linewidth=1.5)

ax.set_title(f'Asymmetric Pressure Index Distributions ({len(bbb_df):,} Audited Deliveries)', 
             fontsize=11, fontweight='bold', color=WHITE, pad=10)
ax.set_xlabel('Pressure Index (0–100 Scale)', fontsize=9, color=GRAY)
ax.set_ylabel('Empirical Density', fontsize=9, color=GRAY)
ax.legend(frameon=True, facecolor=NAVY, edgecolor='#334155', fontsize=7.5, loc='upper left')
ax.grid(True, linestyle=':', alpha=0.25, color=WHITE)
ax.tick_params(colors=GRAY, labelsize=8)

for spine in ax.spines.values():
    spine.set_color('#334155')

plt.tight_layout()
plt.savefig('output/figures/chart1_pressure_distribution.png', facecolor=NAVY)
plt.close()
print("Chart 1 generated: Real Empirical Pressure Distribution")

# -------------------------------------------------------------
# CHART 2: Top 10 Batters Strike Rate Comparison
# -------------------------------------------------------------
top_bat = pd.read_csv('output/Top_10_Batters.csv')

fig, ax = plt.subplots(figsize=(7.5, 4.0), dpi=300)
fig.patch.set_facecolor(NAVY)
ax.set_facecolor(DARK_CARD)

# Invert order for horizontal bar chart (Rank 1 at top)
bat_plot = top_bat.iloc[::-1].reset_index(drop=True)
batters = bat_plot['Player_Name'].tolist()
p_sr = bat_plot['pressure_sr'].tolist()
norm_sr = bat_plot['normal_sr'].tolist()

y = np.arange(len(batters))
height = 0.38

rects1 = ax.barh(y + height/2, p_sr, height, label='Pressure Strike Rate (P >= 50)', color=PINK, edgecolor=NAVY)
rects2 = ax.barh(y - height/2, norm_sr, height, label='Normal Strike Rate (P < 50)', color='#334155', edgecolor=NAVY)

ax.set_title('Top 10 Batters: Pressure Strike Rate vs Personal Baseline', fontsize=11, fontweight='bold', color=WHITE, pad=10)
ax.set_xlabel('Strike Rate', fontsize=9, color=GRAY)
ax.set_yticks(y)
ax.set_yticklabels(batters, fontsize=8.5, color=WHITE)
ax.legend(frameon=True, facecolor=NAVY, edgecolor='#334155', fontsize=8, loc='lower right')
ax.grid(True, axis='x', linestyle=':', alpha=0.25, color=WHITE)
ax.tick_params(colors=GRAY, labelsize=8)

for spine in ax.spines.values():
    spine.set_color('#334155')

plt.tight_layout()
plt.savefig('output/figures/chart2_batters_comparison.png', facecolor=NAVY)
plt.close()
print("Chart 2 generated: Top 10 Batters Strike Rate Comparison")

# -------------------------------------------------------------
# CHART 3: Top 10 Bowlers Economy vs Boundary Conceded %
# -------------------------------------------------------------
top_bowl = pd.read_csv('output/Top_10_Bowlers.csv')

fig, ax = plt.subplots(figsize=(7.5, 4.0), dpi=300)
fig.patch.set_facecolor(NAVY)
ax.set_facecolor(DARK_CARD)

bowlers = top_bowl['Player_Name'].tolist()
econ = top_bowl['pressure_econ'].tolist()
bdry = top_bowl['pressure_bdry_conceded_pct'].tolist()
overs = top_bowl['pressure_overs'].tolist()

# Scaling bubble size
sizes = [max(o * 2.2, 40) for o in overs]

scatter = ax.scatter(econ, bdry, s=sizes, c=overs, cmap='cool', edgecolors=WHITE, linewidth=1.2, alpha=0.85)

for i, txt in enumerate(bowlers):
    ax.annotate(txt, (econ[i], bdry[i]), fontsize=7.5, color=WHITE, weight='bold', xytext=(5, 4), textcoords='offset points')

ax.set_title('Top 10 Bowlers: Pressure Economy vs Boundary Concession %', fontsize=11, fontweight='bold', color=WHITE, pad=10)
ax.set_xlabel('Pressure Economy Rate (Runs/Over, Lower = Better)', fontsize=9, color=GRAY)
ax.set_ylabel('Boundary Conceded % (Lower = Better)', fontsize=9, color=GRAY)
ax.grid(True, linestyle=':', alpha=0.25, color=WHITE)
ax.tick_params(colors=GRAY, labelsize=8)

cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Pressure Overs Bowled (Volume)', fontsize=7.5, color=GRAY)
cbar.ax.tick_params(colors=GRAY, labelsize=7)

for spine in ax.spines.values():
    spine.set_color('#334155')

plt.tight_layout()
plt.savefig('output/figures/chart3_bowlers_scatter.png', facecolor=NAVY)
plt.close()
print("Chart 3 generated: Top 10 Bowlers Scatter Plot")

# -------------------------------------------------------------
# CHART 4: Format Environment Divergence
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.5, 3.2), dpi=300)
fig.patch.set_facecolor(NAVY)
ax1.set_facecolor(DARK_CARD)
ax2.set_facecolor(DARK_CARD)

p_bat_mask = bbb_df['batting_pressure'] >= 50
p_bowl_mask = bbb_df['bowling_pressure'] >= 50
ipl_m = bbb_df['is_ipl']
t20i_m = (bbb_df['match_format'] == 'T20I')

bbb_df['is_batter_ball'] = (bbb_df['extras_type'] != 'wide')

ipl_sr = (bbb_df[p_bat_mask & ipl_m]['runs'].sum() / bbb_df[p_bat_mask & ipl_m]['is_batter_ball'].sum()) * 100.0
t20i_sr = (bbb_df[p_bat_mask & t20i_m]['runs'].sum() / bbb_df[p_bat_mask & t20i_m]['is_batter_ball'].sum()) * 100.0

ipl_econ = (bbb_df[p_bowl_mask & ipl_m]['bowler_runs_conceded'].sum() / (bbb_df[p_bowl_mask & ipl_m]['is_legal_ball'].sum() / 6.0))
t20i_econ = (bbb_df[p_bowl_mask & t20i_m]['bowler_runs_conceded'].sum() / (bbb_df[p_bowl_mask & t20i_m]['is_legal_ball'].sum() / 6.0))

categories = ['IPL (2022-26)', 'T20 Internationals']
sr_vals = [ipl_sr, t20i_sr]
econ_vals = [ipl_econ, t20i_econ]

bars1 = ax1.bar(categories, sr_vals, color=[PINK, CYAN], width=0.5, edgecolor=NAVY)
ax1.set_title('Pressure Strike Rate Environment', fontsize=9.5, fontweight='bold', color=WHITE)
ax1.set_ylabel('Strike Rate', fontsize=8, color=GRAY)
ax1.set_ylim(100, 160)
ax1.grid(True, axis='y', linestyle=':', alpha=0.25, color=WHITE)
ax1.tick_params(colors=GRAY, labelsize=7.5)
for bar in bars1:
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 2, f"{yval:.2f}", ha='center', va='bottom', color=WHITE, fontsize=8, weight='bold')

bars2 = ax2.bar(categories, econ_vals, color=[PINK, CYAN], width=0.5, edgecolor=NAVY)
ax2.set_title('Pressure Economy Environment', fontsize=9.5, fontweight='bold', color=WHITE)
ax2.set_ylabel('Runs Per Over', fontsize=8, color=GRAY)
ax2.set_ylim(6, 11)
ax2.grid(True, axis='y', linestyle=':', alpha=0.25, color=WHITE)
ax2.tick_params(colors=GRAY, labelsize=7.5)
for bar in bars2:
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 0.15, f"{yval:.2f}", ha='center', va='bottom', color=WHITE, fontsize=8, weight='bold')

for a in [ax1, ax2]:
    for spine in a.spines.values():
        spine.set_color('#334155')

plt.tight_layout()
plt.savefig('output/figures/chart4_format_divergence.png', facecolor=NAVY)
plt.close()
print("Chart 4 generated: Format Environment Divergence")

print("\nALL 4 PUBLICATION FIGURES GENERATED SUCCESSFULLY IN output/figures/")
