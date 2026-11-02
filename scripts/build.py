"""US public prekindergarten and kindergarten enrollment by state, fall 2010 to fall 2022,
plus the share of 3- to 5-year-olds enrolled in school by state, 2021 to 2023.

Sources (all U.S. Department of Education, NCES, Digest of Education Statistics):
  Table 203.40 / 203.45, Enrollment in public elementary and secondary schools, by level, grade, and state
  (Common Core of Data, State Nonfiscal Survey), Digest editions 2013 to 2023, one fall per table.
  Table 202.25, Percentage of 3- to 5-year-old children enrolled in school, by state (Census Bureau ACS 1-year PUMS),
  Digest editions 2022 to 2024.
Input: raw/dYY_203.40.xls(x), raw/dYY_203.45.xls(x), raw/dYY_202.25.xlsx downloaded from
       https://nces.ed.gov/programs/digest/dYY/tables/xls/tabnNNN.NN.xls(x)
"""
import os, re, glob, numpy as np, pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'raw'); OUT = os.path.join(ROOT, 'data'); os.makedirs(OUT, exist_ok=True)
STATES = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'District of Columbia',
          'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland',
          'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire',
          'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania',
          'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington',
          'West Virginia', 'Wisconsin', 'Wyoming']
ABBR = dict(zip(STATES, ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
                         'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
                         'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']))
ABBR['United States'] = 'US'
GRADES = ['Prekindergarten', 'Kindergarten'] + [f'Grade {i}' for i in range(1, 13)]


def clean_name(v):
    v = re.sub(r'\\\d+(,\d+)*\\', '', str(v)).replace('…', '')
    return re.sub(r'\.{2,}.*$', '', v).strip().strip('.').strip()


def tonum(v):
    try:
        x = float(str(v).replace(',', ''))
        return x
    except ValueError:
        return np.nan


def parse_enrollment(path):
    x = pd.read_excel(path, header=None)
    fall = int(re.search(r'Fall (\d{4})', str(x.iloc[0, 0])).group(1))
    norm = lambda v: re.sub(r'\\.*', '', str(v)).replace('-', '').strip()
    hr = next(i for i in range(12) if 'Kindergarten' in [norm(v) for v in x.iloc[i].tolist()])
    hdr = [norm(v) for v in x.iloc[hr].tolist()]
    top = [str(v).strip() for v in x.iloc[hr - 1].tolist()]
    cols = {}
    for j, h in enumerate(hdr):
        if h in GRADES and h not in cols: cols[h] = j
        if (h.startswith('Total, all grades') or top[j].startswith('Total, all grades')) and 'total' not in cols: cols['total'] = j
    foot = {}
    for i in range(len(x)):
        m = re.match(r'^\\(\d+)\\(.+)$', str(x.iloc[i, 0]).strip())
        if m: foot[m.group(1)] = m.group(2).strip()
    rows = []
    for i in range(hr + 1, len(x)):
        name = clean_name(x.iloc[i, 0])
        if name not in STATES and name != 'United States': continue
        r = {'fall_year': fall, 'state': name, 'state_abbr': ABBR[name]}
        notes = []
        for k, j in cols.items():
            v = tonum(x.iloc[i, j])
            nxt = x.iloc[i, j + 1] if j + 1 < x.shape[1] else None
            if np.isnan(v) and nxt is not None and not np.isnan(tonum(nxt)) and hdr[j + 1] in ('', 'nan', hdr[j]):
                v = tonum(nxt)
            raw = [str(x.iloc[i, j])] + ([str(nxt)] if nxt is not None and hdr[j + 1] in ('', 'nan', hdr[j]) else [])
            mk = [m for m in raw if m not in ('nan',) and np.isnan(tonum(m))]
            if mk and k in ('Prekindergarten', 'Kindergarten'):
                txt = ' '.join(foot.get(n, n) for m_ in mk for n in re.findall(r'\d+', m_))
                notes.append(f'{k}: {txt}')
            key = {'total': 'total_all_grades', 'Prekindergarten': 'prekindergarten', 'Kindergarten': 'kindergarten'}.get(k, k.lower().replace(' ', '_'))
            r[key] = v
        r['source_note'] = '; '.join(notes)
        r['source_table'] = f'Digest {os.path.basename(path)[1:3]} table {os.path.basename(path)[4:10]}'
        rows.append(r)
    return pd.DataFrame(rows)


frames = [parse_enrollment(f) for f in sorted(glob.glob(f'{RAW}/d*_203.4*.xls*'))]
en = pd.concat(frames, ignore_index=True)
# one row per fall and state: prefer the most recent Digest edition that reports that fall
en['_ed'] = en.source_table.str.extract(r'Digest (\d+)').astype(int)
en = en.sort_values(['fall_year', 'state', '_ed']).drop_duplicates(['fall_year', 'state'], keep='last').drop(columns='_ed')
gcols = ['total_all_grades', 'prekindergarten', 'kindergarten'] + [f'grade_{i}' for i in range(1, 13)]
en = en[['fall_year', 'state', 'state_abbr'] + gcols + ['source_note', 'source_table']]
for c in gcols: en[c] = en[c].round().astype('Int64')
en.to_csv(f'{OUT}/public_enrollment_by_state_and_grade_2010_2022.csv', index=False)

pk = en[['fall_year', 'state', 'state_abbr', 'prekindergarten', 'kindergarten', 'total_all_grades', 'source_note']].copy()
pk['prek_per_100_kindergartners'] = (100 * pk.prekindergarten / pk.kindergarten).round(1)
pk['prek_share_of_enrollment_pct'] = (100 * pk.prekindergarten / pk.total_all_grades).round(2)
base = pk[pk.fall_year == 2012].set_index('state').prekindergarten
pk['prek_change_since_2012_pct'] = pk.apply(lambda r: round(100 * (r.prekindergarten / base[r.state] - 1), 1) if base.get(r.state) else np.nan, axis=1)
pk.to_csv(f'{OUT}/prek_and_kindergarten_by_state.csv', index=False)

us = pk[pk.state == 'United States'][['fall_year', 'prekindergarten', 'kindergarten', 'total_all_grades', 'prek_per_100_kindergartners', 'prek_share_of_enrollment_pct']]
us.to_csv(f'{OUT}/national_prek_kindergarten.csv', index=False)

# 3- to 5-year-olds enrolled in school, by state (ACS)
rows = []
for f in sorted(glob.glob(f'{RAW}/d*_202.25.xlsx')):
    x = pd.read_excel(f, header=None)
    year = int(re.search(r': (\d{4})', str(x.iloc[0, 0])).group(1))
    ages = '3 to 5' if '3- to 5-year-old' in str(x.iloc[0, 0]) else '3 and 4'
    for i in range(len(x)):
        name = clean_name(x.iloc[i, 0])
        if name not in STATES and name != 'United States': continue
        p = tonum(x.iloc[i, 1]); se = tonum(str(x.iloc[i, 3]).strip('()'))
        rows.append({'year': year, 'state': name, 'state_abbr': ABBR[name], 'age_group': ages, 'percent_enrolled_in_school': round(p, 1),
                     'standard_error': round(se, 2), 'source_table': f'Digest {os.path.basename(f)[1:3]} table 202.25'})
rate = pd.DataFrame(rows).sort_values(['year', 'state'])
rate.to_csv(f'{OUT}/children_3_to_5_enrolled_by_state_2021_2023.csv', index=False)

print(en.groupby('fall_year').size().to_string())
print(us.to_string(index=False))
print(en[en.source_note != ''][['fall_year', 'state', 'prekindergarten', 'kindergarten', 'source_note']].to_string(index=False))
print(rate.groupby('year').size(), rate[rate.state == 'United States'])
chk = en[en.state != 'United States'].groupby('fall_year')[['prekindergarten', 'kindergarten', 'total_all_grades']].sum()
print((chk - en[en.state == 'United States'].set_index('fall_year')[['prekindergarten', 'kindergarten', 'total_all_grades']]).to_string())
