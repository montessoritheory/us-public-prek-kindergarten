"""Charts and cover for the US public pre-K and kindergarten dataset. Run after build.py."""
import os, numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.colors import LinearSegmentedColormap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = f'{ROOT}/data'; IMG = f'{ROOT}/images'; os.makedirs(IMG, exist_ok=True)
FONTS = os.environ.get('FONT_DIR', os.path.join(ROOT, 'scripts', 'fonts'))
for f in os.listdir(FONTS):
    if f.endswith('.ttf'): fm.fontManager.addfont(f'{FONTS}/{f}')
SERIF, SANS = 'Fraunces', 'DM Sans 9pt'
CREAM, INK, MUTED, GRID = '#F7F3EC', '#2B2A28', '#6B6862', '#E4DED3'
TC, BLUE, OLIVE, GOLD = '#B4532F', '#1F72B8', '#7F9A1F', '#D19A2A'
plt.rcParams.update({'font.family': SANS, 'font.size': 13, 'axes.edgecolor': GRID, 'axes.labelcolor': MUTED,
                     'xtick.color': MUTED, 'ytick.color': MUTED, 'axes.facecolor': CREAM, 'figure.facecolor': CREAM,
                     'axes.spines.top': False, 'axes.spines.right': False, 'axes.grid': True, 'grid.color': GRID,
                     'grid.linewidth': 0.8, 'axes.axisbelow': True})
SRC = 'Source: NCES Digest of Education Statistics, tables 203.40, 203.45 and 202.25. Dataset by Montessori Theory (montessori-theory.com), CC BY 4.0.'
# tile grid (column, row) for the 50 states and DC
TILE = {'AK': (0, 0), 'ME': (11, 0), 'VT': (10, 1), 'NH': (11, 1), 'WA': (1, 2), 'ID': (2, 2), 'MT': (3, 2), 'ND': (4, 2), 'MN': (5, 2),
        'IL': (6, 2), 'WI': (7, 2), 'MI': (8, 2), 'NY': (9, 2), 'RI': (10, 2), 'MA': (11, 2), 'OR': (1, 3), 'NV': (2, 3), 'WY': (3, 3),
        'SD': (4, 3), 'IA': (5, 3), 'IN': (6, 3), 'OH': (7, 3), 'PA': (8, 3), 'NJ': (9, 3), 'CT': (10, 3), 'CA': (1, 4), 'UT': (2, 4),
        'CO': (3, 4), 'NE': (4, 4), 'MO': (5, 4), 'KY': (6, 4), 'WV': (7, 4), 'VA': (8, 4), 'MD': (9, 4), 'DE': (10, 4), 'AZ': (2, 5),
        'NM': (3, 5), 'KS': (4, 5), 'AR': (5, 5), 'TN': (6, 5), 'NC': (7, 5), 'SC': (8, 5), 'DC': (9, 5), 'OK': (4, 6), 'LA': (5, 6),
        'MS': (6, 6), 'AL': (7, 6), 'GA': (8, 6), 'HI': (0, 7), 'TX': (4, 7), 'FL': (9, 7)}
CMAP = LinearSegmentedColormap.from_list('mt', ['#F3E3D3', '#E2A47F', TC, '#6E2E17'])


def finish(fig, title, sub, path):
    fig.text(0.06, 0.94, title, family=SERIF, weight=800, size=26, color=INK, va='top')
    fig.text(0.06, 0.875, sub, size=14, color=MUTED, va='top')
    fig.text(0.06, 0.03, SRC, size=10, color=MUTED)
    fig.savefig(path, dpi=150); plt.close(fig)


def tilemap(ax, values, vmin, vmax, fmt):
    for ab, (c, r) in TILE.items():
        v = values.get(ab, np.nan)
        col = CMAP((v - vmin) / (vmax - vmin)) if not np.isnan(v) else '#DDD8CF'
        ax.add_patch(plt.Rectangle((c, -r), 0.92, 0.92, color=col, lw=0))
        light = np.isnan(v) or (v - vmin) / (vmax - vmin) < 0.45
        ax.text(c + 0.46, -r + 0.58, ab, ha='center', va='center', size=12, weight='bold', color=INK if light else 'white')
        ax.text(c + 0.46, -r + 0.28, fmt(v) if not np.isnan(v) else 'n/a', ha='center', va='center', size=9.5, color=INK if light else 'white')
    ax.set_xlim(-0.2, 12.2); ax.set_ylim(-7.2, 1.1); ax.set_aspect('equal'); ax.axis('off')


pk = pd.read_csv(f'{D}/prek_and_kindergarten_by_state.csv')
us = pd.read_csv(f'{D}/national_prek_kindergarten.csv')
rate = pd.read_csv(f'{D}/children_3_to_5_enrolled_by_state_2021_2023.csv')

# 1. national trend
fig = plt.figure(figsize=(12, 6.5)); ax = fig.add_axes([0.09, 0.16, 0.8, 0.63])
ax.plot(us.fall_year, us.prekindergarten / 1e6, color=TC, lw=2.6, marker='o', ms=6, mec=CREAM, mew=1.5)
ax.plot(us.fall_year, us.kindergarten / 1e6, color=BLUE, lw=2.6, marker='o', ms=6, mec=CREAM, mew=1.5)
ax.text(2022.3, us.prekindergarten.iloc[-1] / 1e6, 'Prekindergarten', color=INK, size=12, va='center')
ax.text(2022.3, us.kindergarten.iloc[-1] / 1e6, 'Kindergarten', color=INK, size=12, va='center')
ax.annotate('Fall 2020, first school\nyear of the pandemic', xy=(2020, us.loc[us.fall_year == 2020, 'prekindergarten'].iloc[0] / 1e6),
            xytext=(2016.2, 2.2), size=11, color=MUTED, arrowprops=dict(arrowstyle='-', color=MUTED, lw=0.8))
ax.set_ylim(0, 4.3); ax.set_xlim(2009.5, 2025); ax.set_xticks(range(2010, 2023, 2)); ax.set_ylabel('Students, millions')
finish(fig, 'Public prekindergarten and kindergarten, 2010-2022',
       f'Public pre-K grew from {us.prekindergarten.iloc[0]/1e6:.2f} to {us.prekindergarten.iloc[-1]/1e6:.2f} million students, fall enrollment',
       f'{IMG}/national_trend.png')

# 2. pre-K per 100 kindergartners, tile map 2022
l = pk[(pk.fall_year == 2022) & (pk.state != 'United States')].set_index('state_abbr').prek_per_100_kindergartners
fig = plt.figure(figsize=(12, 8)); ax = fig.add_axes([0.05, 0.08, 0.9, 0.76])
tilemap(ax, l.to_dict(), 0, 110, lambda v: f'{v:.0f}')
finish(fig, 'Public pre-K students for every 100 kindergartners', 'Fall 2022, public schools. Higher means a larger public pre-K system',
       f'{IMG}/prek_per_100_kindergartners_map_2022.png')

# 3. top and bottom states, pre-K per 100 kindergartners
s = pk[(pk.fall_year == 2022) & (pk.state != 'United States')].sort_values('prek_per_100_kindergartners', ascending=False)
top = s.head(15).iloc[::-1]
fig = plt.figure(figsize=(12, 7.5)); ax = fig.add_axes([0.22, 0.14, 0.7, 0.67])
ax.barh(top.state, top.prek_per_100_kindergartners, color=TC, height=0.68)
for y, v in enumerate(top.prek_per_100_kindergartners): ax.text(v + 1, y, f'{v:.0f}', va='center', size=11, color=INK)
ax.grid(axis='y', visible=False); ax.set_xlabel('Public pre-K students per 100 public kindergartners, fall 2022')
finish(fig, 'States with the largest public pre-K', 'The 15 states with the most public pre-K students relative to kindergarten', f'{IMG}/top_states_2022.png')

# 4. 3- to 5-year-olds enrolled in school, tile map 2023
r = rate[(rate.year == 2023) & (rate.state != 'United States')].set_index('state_abbr').percent_enrolled_in_school
fig = plt.figure(figsize=(12, 8)); ax = fig.add_axes([0.05, 0.08, 0.9, 0.76])
tilemap(ax, r.to_dict(), 40, 75, lambda v: f'{v:.0f}%')
usr = rate[(rate.year == 2023) & (rate.state == 'United States')].percent_enrolled_in_school.iloc[0]
finish(fig, 'Young children enrolled in school, by state', f'Percent of 3- to 5-year-olds enrolled in preschool, kindergarten or school, 2023 (US {usr:.0f}%)',
       f'{IMG}/enrolled_3_to_5_map_2023.png')

# cover
fig = plt.figure(figsize=(16, 8), dpi=100)
ax = fig.add_axes([0.5, 0.1, 0.48, 0.78]); tilemap(ax, l.to_dict(), 0, 110, lambda v: f'{v:.0f}')
fig.text(0.05, 0.80, 'US Public Pre-K', family=SERIF, weight=800, size=52, color=TC, va='top')
fig.text(0.05, 0.67, 'and Kindergarten', family=SERIF, weight=800, size=52, color=TC, va='top')
fig.text(0.05, 0.53, 'By state, fall 2010 to fall 2022', family=SERIF, weight=600, size=30, color=INK, va='top')
for i, t in enumerate(['Enrollment by grade for all 50 states and DC', f'{us.prekindergarten.iloc[-1]/1e6:.2f} million public pre-K students in fall 2022',
                       'Plus the share of 3- to 5-year-olds in school, 2021-2023']):
    fig.text(0.05, 0.40 - i * 0.065, t, size=18, color=INK, va='top')
fig.text(0.62, 0.06, 'Public pre-K students per 100 kindergartners, fall 2022', size=13, color=MUTED)
fig.text(0.05, 0.08, 'Montessori Theory  ·  montessori-theory.com  ·  CC BY 4.0', size=15, color=MUTED, family=SERIF, weight=600)
fig.savefig(f'{IMG}/cover.png', dpi=100); plt.close(fig)
print(s.head(10)[['state', 'prekindergarten', 'kindergarten', 'prek_per_100_kindergartners']].to_string(index=False))
print(s.tail(5)[['state', 'prekindergarten', 'kindergarten', 'prek_per_100_kindergartners']].to_string(index=False))
