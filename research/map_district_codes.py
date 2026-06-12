"""
Map PLFS district sequential codes to Census/standard district names
for Bihar and Rajasthan by matching record counts between 2019-20 and Census 2011.

Strategy:
  1. Get PLFS 2019-20 Bihar district codes + record counts
  2. Get PLFS 2019-20 Rajasthan district codes + record counts
  3. Get PLFS 2023-24 Bihar district codes + record counts (2023 has dist_code_perrv)
  4. Map code 1..N to district names using alphabetical ordering of Census names
     (PLFS uses alphabetical ordering within state for sequential codes)
"""
import pandas as pd, zipfile, numpy as np

def get_plfs_dist_counts(zip_path, inner_file, state_col, dist_col, state_code):
    with zipfile.ZipFile(zip_path) as z:
        with z.open(inner_file) as f:
            df = pd.read_csv(f, low_memory=False, usecols=[state_col, dist_col])
    s = pd.to_numeric(df[state_col], errors='coerce')
    sub = df[s == state_code].copy()
    counts = sub.groupby(dist_col).size().reset_index()
    counts.columns = ['plfs_code', 'n']
    counts = counts.sort_values('plfs_code').reset_index(drop=True)
    return counts

# Load Census names for Bihar and Rajasthan
census = pd.read_excel('database/seeds/DDW_PCA0000_2011_Indiastatedist.xlsx',
                       sheet_name='Sheet1', dtype=str)

for state_str, state_code_int, state_name in [('10', 10, 'Bihar'), ('08', 8, 'Rajasthan')]:
    print(f"\n{'='*60}")
    print(f"{state_name} PLFS Code Mapping")
    print(f"{'='*60}")

    census_dists = census[(census['State']==state_str) & (census['Level']=='DISTRICT') & (census['TRU']=='Total')]
    census_names = sorted(census_dists['Name'].tolist())
    print(f"Census districts (alphabetical): {len(census_names)}")

    # PLFS 2019-20 codes
    c19 = get_plfs_dist_counts(
        'data/raw/plfs/CSV_PLFS_19_20.zip',
        f'CSV_PLFS_19_20/PERRV_2019-20.csv',
        'state_per_rv', 'district_per_rv', state_code_int
    )
    print(f"PLFS 2019-20 district codes: {sorted(c19['plfs_code'].tolist())}")

    # PLFS 2023-24 codes (labelled as dist_code_perrv — confirmed correct)
    c23 = get_plfs_dist_counts(
        'data/raw/plfs/CSV_data_PLFS_2023_2024.zip',
        'CSV_data_PLFS_2023_2024/perrv.csv',
        'state_perrv', 'dist_code_perrv', state_code_int
    )
    print(f"PLFS 2023-24 district codes: {sorted(c23['plfs_code'].tolist())}")

    # Build mapping: PLFS assumes alphabetical ordering of districts
    # So code 1 = first alphabetically, code 2 = second, etc.
    n_census = len(census_names)
    n_plfs19 = len(c19)

    print(f"\nDistrict code → Census name mapping (2019-20, alphabetical assumption):")
    mapping_rows = []
    for i, row in c19.iterrows():
        code = int(row['plfs_code'])
        # Alphabetical mapping: code 1 = index 0, code 2 = index 1, etc.
        census_idx = code - 1
        census_name = census_names[census_idx] if census_idx < len(census_names) else "OUT_OF_RANGE"
        n23_match = c23[c23['plfs_code']==code]['n'].values
        n23 = int(n23_match[0]) if len(n23_match) else 0
        mapping_rows.append({'plfs_code': code, 'census_name_alpha': census_name,
                              'n_2019': int(row['n']), 'n_2023': n23})
        print(f"  Code {code:2d}: {census_name:<30} | n19={int(row['n']):5d} | n23={n23:5d}")

    pd.DataFrame(mapping_rows).to_csv(
        f'research/{state_name.lower()}_plfs_code_mapping.csv', index=False)
    print(f"\nSaved: research/{state_name.lower()}_plfs_code_mapping.csv")
