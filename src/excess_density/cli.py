import re
import typer
from pathlib import Path
import json
from .data_model import MixtureRecord
from pydantic import ValidationError
import pandas as pd
from itertools import chain

app = typer.Typer()


def _validate_file(file: Path):
    with open(file, "r") as fid:
        data = json.load(fid)
    record = MixtureRecord.val(**data)


@app.command()
def validate(file: Path):
    if file.is_file():
        MixtureRecord.parse_jsonfile(file)
    elif file.is_dir():
        for f in file.glob("**/*.json"):
            try:
                MixtureRecord.parse_jsonfile(f)
            except ValidationError as e:
                print(f)
                print(e)


@app.command()
def cat(file: Path):
    assert file.is_file()
    print(MixtureRecord.parse_jsonfile(file))

def compute_wide_dataframe_rowwise(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute a wide-format DataFrame with computed mixture properties,
    now also handling cases where only 'excess molar volume' is provided.

    Steps:
    1. Pivot long-form to wide by ['inchi_key1','inchi_key2','temperature','x1','x2'].
    2. Merge metadata and pure-component densities/molecular weights.
    3. Override pure densities from rows where x1==1 or x2==1.
    4. Compute static columns: mixture MW and ideal density.
    5. Row-wise compute missing:
       - If density missing and 'excess molar volume' present:
           * compute mixture density via V_mix = V_id + V_ex, density = MW_mix / V_mix
       - density (from ideal + excess density) if still missing
       - excess density (from density – ideal density)
       - mixture molar density, pure molar densities, ideal molar density
       - excess molar density (from mixture molar – ideal molar)
    6. Rename computed columns:
       - 'ideal density' -> 'ideal_density'
       - 'density', 'excess density', 'excess molar density' include their units
    Returns:
        df_wide with columns:
        ['inchi_key1','inchi_key2','temperature','x1','x2',
         'doi','smi1','smi2','name1','name2',
         'molecular_weight1','molecular_weight2',
         'ideal_density','density [unit]','excess density [unit]','excess molar density [unit]']
    """
    # Define keys and metadata
    keys = ['inchi_key1', 'inchi_key2', 'temperature', 'x1', 'x2']
    meta_cols = ['doi', 'smi1', 'smi2', 'name1', 'name2',
                 'molecular_weight1', 'molecular_weight2']

    # Map measurement to its units
    units_map = (
        df[['measurement', 'measurement_units']]
          .drop_duplicates()
          .set_index('measurement')['measurement_units']
          .to_dict()
    )

    # Pivot measurements to wide; this includes 'excess molar volume' if present
    df_wide = df.pivot_table(index=keys, columns='measurement', values='value').reset_index()

    # Merge in metadata and original pure densities
    extras = (
        df.drop_duplicates(subset=keys)
          .loc[:, keys + meta_cols + ['density1 [g/cm^3]', 'density2 [g/cm^3]']]
    )
    df_wide = df_wide.merge(extras, on=keys, how='left')

    pure1_map = (
        df.loc[(df.measurement=="density") & (df.x1==1.0)]
          .set_index(['inchi_key1','inchi_key2','temperature'])['value']
    )
    pure2_map = (
        df.loc[(df.measurement=="density") & (df.x2==1.0)]
          .set_index(['inchi_key1','inchi_key2','temperature'])['value']
    )

    def fill_pure(row):
        key = (row['inchi_key1'], row['inchi_key2'], row['temperature'])
        # override density1 from mixture endpoints if available
        if key in pure1_map:
            row['density1 [g/cm^3]'] = pure1_map[key]
        # override density2 from mixture endpoints if available
        if key in pure2_map:
            row['density2 [g/cm^3]'] = pure2_map[key]
        return row

    df_wide = df_wide.apply(fill_pure, axis=1)


    # Compute mixture molecular weight and ideal density
    df_wide['mw_mix'] = (
        df_wide['x1'] * df_wide['molecular_weight1'] +
        df_wide['x2'] * df_wide['molecular_weight2']
    )
    df_wide['ideal density'] = (
        df_wide['x1'] * df_wide['density1 [g/cm^3]'] +
        df_wide['x2'] * df_wide['density2 [g/cm^3]']
    )

    # Row-wise computation
    def compute_row(row):
        # Handle case: only excess molar volume provided
        if pd.isna(row.get('density')) and not pd.isna(row.get('excess molar volume')):
            # Compute pure molar volumes (cm3/mol)
            V1 = row['molecular_weight1'] / row['density1 [g/cm^3]']
            V2 = row['molecular_weight2'] / row['density2 [g/cm^3]']
            V_id = row['x1'] * V1 + row['x2'] * V2
            V_mix = V_id + row['excess molar volume']
            # Compute mixture density (g/cm3)
            row['density'] = row['mw_mix'] / V_mix

        # Compute density if still missing via excess density
        if pd.isna(row.get('density')) and not pd.isna(row.get('excess density')):
            row['density'] = row['ideal density'] + row['excess density']

        # Compute excess density if missing
        if pd.isna(row.get('excess density')) and not pd.isna(row.get('density')):
            row['excess density'] = row['density'] - row['ideal density']

        # Compute molar densities
        row['mixture molar volume'] = row["mw_mix"] / row['density']
        row['pure1 molar volume'] = row['molecular_weight1'] / row['density1 [g/cm^3]']
        row['pure2 molar volume'] = row['molecular_weight2'] / row['density2 [g/cm^3]']
        row['ideal molar volume'] = (
            row['x1'] * row['pure1 molar volume'] +
            row['x2'] * row['pure2 molar volume']
        )

        # Compute excess molar density
        if pd.isna(row.get('excess molar volume')):
            row['excess molar volume'] = (
                row['mixture molar volume'] - row['ideal molar volume']
            )
        return row

    df_wide = df_wide.apply(compute_row, axis=1)

    # Rename computed columns to include units
    rename_map = {'ideal density': 'ideal_density'}
    for meas in ['density', 'excess density', 'excess molar volume']:
        if meas in df_wide.columns:
            unit = units_map.get(meas, units_map.get('density', ''))
            if meas == 'excess molar density' and not units_map.get(meas):
                unit = 'mol/cm^3'
            rename_map[meas] = f"{meas} [{unit}]"

    df_wide = df_wide.rename(columns=rename_map)
    return df_wide

def report_missing_entities(df_wide: pd.DataFrame) -> pd.DataFrame:
    """
    Identify unique (doi, smi1, smi2) entities where every row
    lacks all three key measurements: density, excess density,
    and excess molar density.
    """
    # Regex to match our three target columns with units
    pattern = re.compile(r'^(density|excess density|excess molar density) \[.*\]$')
    meas_cols = [c for c in df_wide.columns if pattern.match(c)]

    # Group and check if all values in these columns are NaN
    grouped = df_wide.groupby(['doi', 'smi1', 'smi2'])
    missing = grouped.apply(lambda g: g[meas_cols].isna().all().all())
    missing_entities = missing[missing].reset_index()[['doi', 'smi1', 'smi2']]
    return missing_entities

def report_missing_entities_with_examples(df_wide: pd.DataFrame) -> pd.DataFrame:
    """
    For each (doi, smi1, smi2) group where all key measurements
    (density, excess density, excess molar density) are missing,
    return one example row from that group.
    """
    # Identify the measurement columns (they include units in the heading)
    pattern = re.compile(r'^(density|excess density|excess molar density) \[.*\]$')
    meas_cols = [c for c in df_wide.columns if pattern.match(c)]

    # Determine which groups are entirely missing those measurements
    group_missing = (
        df_wide
        .groupby(['doi', 'smi1', 'smi2'])[meas_cols]
        .apply(lambda g: g.isna().to_numpy().all())
    )

    # Extract the index tuples (doi, smi1, smi2) for missing groups
    missing_groups = [idx for idx, is_missing in group_missing.items() if is_missing]

    # Collect one example row per missing group
    examples = []
    for doi, smi1, smi2 in missing_groups:
        subset = df_wide[
            (df_wide['doi'] == doi) &
            (df_wide['smi1'] == smi1) &
            (df_wide['smi2'] == smi2)
        ]
        if not subset.empty:
            examples.append(subset.iloc[0])

    return pd.DataFrame(examples).reset_index(drop=True)


def report_complete_counts(df_wide: pd.DataFrame) -> pd.DataFrame:
    """
    For each (doi, smi1, smi2) group, count how many rows have
    non-null values in all three measurements:
      - density [unit]
      - excess density [unit]
      - excess molar density [unit]
    Returns a DataFrame with columns: doi, smi1, smi2, complete_records.
    """
    # Identify the three measurement columns (they include units in the heading)
    pattern = re.compile(r'^(density|excess density|excess molar density) \[.*\]$')
    meas_cols = [c for c in df_wide.columns if pattern.match(c)]

    # Boolean mask of rows that are “complete” (no NaNs in those columns)
    is_complete = df_wide[meas_cols].notna().all(axis=1)

    # Count completes per group
    counts = (
        df_wide[is_complete]
        .groupby(['doi', 'smi1', 'smi2'])
        .size()
        .reset_index(name='complete_records')
    )

    # Ensure every group appears, filling zeros where needed
    all_groups = (
        df_wide[['doi', 'smi1', 'smi2']]
        .drop_duplicates()
    )
    result = (
        all_groups
        .merge(counts, on=['doi', 'smi1', 'smi2'], how='left')
        .fillna({'complete_records': 0})
        .astype({'complete_records': int})
    )
    result = result.sort_values(
        by=['complete_records', 'doi'],
        ascending=[False, True]
    ).reset_index(drop=True)
    return result


@app.command()
def export(path: Path, output: Path):
    if path.is_dir():
        files = chain(path.glob("**/*.jsonc"), path.glob("**/*.json"))
    else:
        files = [path]

    records = []
    for file in files:
        mr = MixtureRecord.parse_jsonfile(file)
        records.extend(mr.as_records("K"))
    df = pd.DataFrame(records)
    df = compute_wide_dataframe_rowwise(df)
    df.round(4).to_csv(output)
