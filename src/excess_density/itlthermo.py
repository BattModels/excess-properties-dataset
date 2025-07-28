import html
import logging
import re

import ilthermopy as ilt
import pandas as pd
import requests
from tqdm import tqdm

from .data_model import (
    MixtureDatum,
    MixtureRecord,
    PressureMeasurement,
    TemperatureMeasurement,
)

# Define properties of interest
PROPERTY_MAP = {
    "enthalpy": "molar enthalpy",
    "excess volume": "excess molar volume",
}


def is_expected_property(property: str, target: str):
    expected_properties = {
        "Density": {"Specific density"},
    }
    if property == target:
        return True
    elif alt := expected_properties.get(target, None):
        return property in alt
    return False


def split_column_with_unit(df: pd.DataFrame, pattern: str) -> pd.DataFrame:
    # Find the first column matching the pattern
    matches = [col for col in df.columns if re.fullmatch(pattern, col)]
    if not matches:
        raise ValueError(f"No column matches pattern: {pattern}")
    if len(matches) > 1:
        raise ValueError(f"Multiple columns matched pattern: {matches}")

    column = matches[0]

    # Extract base and unit
    if ", " not in column:
        raise ValueError(
            f"Matched column '{column}' does not contain a unit (comma-separated)."
        )

    base, unit = column.split(", ")
    base_col = base.strip().lower()
    unit_col = f"{base_col}_unit"

    df[base_col] = df[column]
    df[unit_col] = unit
    df = df.drop(columns=[column])

    return df


def extract_composition_info(df: pd.DataFrame) -> pd.DataFrame:
    """
    Finds the column representing mole or mass fraction of cmp1/cmp2,
    and produces two new columns:
    - x1: the fraction of cmp1 (computed as 1 - x2 if cmp2 is given)
    - xtype: the type of fraction ("mole fraction" or "mass fraction")

    The original composition column is dropped.
    """
    pattern = re.compile(r"(Mole|Weight) fraction of (cmp[12]).*", re.IGNORECASE)

    # Find matching column
    matches = [col for col in df.columns if pattern.fullmatch(col)]
    if not matches:
        raise ValueError("No composition column found.")
    if len(matches) > 1:
        raise ValueError(f"Multiple matching composition columns found: {matches}")

    col = matches[0]
    match = pattern.fullmatch(col)
    fraction_type_raw, component = match.groups()

    # Normalize type string
    xtype = "mole fraction" if fraction_type_raw.lower() == "mole" else "mass fraction"

    # Get values from matched column
    values = df[col]

    # Compute x1
    if component == "cmp1":
        df["x1"] = values
    else:
        df["x1"] = 1.0 - values
    df["x1"] = df["x1"].round(4)

    # Store fraction type
    df["xtype"] = xtype

    # Drop original column
    df = df.drop(columns=[col])

    return df


def get_doi_from_citation(citation: str) -> str | None:
    """
    Given a raw citation string, attempts to find the DOI via CrossRef.
    """
    # Remove excessive punctuation and normalize whitespace
    cleaned = re.sub(r"[.;]", " ", citation)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    # Query CrossRef
    url = "https://api.crossref.org/works"
    params = {"query.bibliographic": cleaned, "rows": 1}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        items = data.get("message", {}).get("items", [])

        if items:
            return items[0].get("DOI", None)
        else:
            return None
    except Exception as e:
        logging.warning(f"Failed to fetch DOI from CrossRef: {e}")
        return None


def extract_entry(entry_id, prop_query):
    entry = ilt.data_structs.GetEntry(entry_id)
    if not is_expected_property(entry.property, prop_query):
        logging.warning(
            f"Skipping {entry_id} because property {entry.property} does not match {prop_query}"
        )
        return None

    header_dict = entry.header
    entry_df = entry.data
    entry_df = entry_df.rename(columns=header_dict)

    entry_df["doi"] = get_doi_from_citation(entry.ref.full)
    entry_df["itltermo_id"] = entry.id
    entry_df["citation"] = entry.ref.full

    re_power = re.compile(r"<SUP>([+-]?\d+)</SUP>")

    cmp_to_name = {}
    name_to_cmp = {}

    entry_df["num_phases"] = len(entry.phases)
    for i, component in enumerate(entry.components):
        entry_df[f"smi{i + 1}"] = component.smiles
        entry_df[f"name{i + 1}"] = component.name

        cmp_to_name[f"cmp{i + 1}"] = component.name
        name_to_cmp[component.name] = f"cmp{i + 1}"

    if entry.solvent is not None:
        solvents = entry.solvent.split(" + ")
        solvents = [name_to_cmp[name] for name in solvents]
    else:
        solvents = None

    new_columns = {}
    for col in entry_df.columns:
        # Renaming
        new_col = col
        for component in entry.components:
            if component.name in col:
                entry_df = entry_df.rename(
                    columns={
                        col: re.sub(
                            re.escape(component.name), name_to_cmp[component.name], col
                        )
                    }
                )

        if new_col != col:
            new_columns[col] = new_col

        if prop_query in col or (prop_query == "Density" and "Specific density" in col):
            entry_df["property"] = prop_query
            entry_df = entry_df.rename(columns={col: "value"})

            match = re.search(r",\s*(.*?)\s*=>", col)
            if match:
                unit = html.unescape(match.group(1))
                unit = re_power.sub(r"**\1", unit)
                entry_df["unit"] = unit

        if "Error" in col:
            entry_df = entry_df.rename(columns={col: "error"})

    entry_df = entry_df.rename(columns=new_columns)
    entry_df = split_column_with_unit(entry_df, r"(?i)temperature.*")
    entry_df = split_column_with_unit(entry_df, r"(?i)pressure.*")
    entry_df = extract_composition_info(entry_df)

    for col in entry_df.columns:
        for component in entry.components:
            if component.name in col:
                logging.warning(f"Did not work: {col}")

    columns = [
        "doi",
        "itltermo_id",
        "citation",
        "property",
        "value",
        "unit",
        "temperature",
        "temperature_unit",
        "pressure",
        "pressure_unit",
        "x1",
        "xtype",
    ]
    for i in range(1, 3):
        columns.extend([f"smi{i}", f"name{i}"])
    return entry_df[columns]


def df_to_mixture_records(df: pd.DataFrame):
    """
    Convert a DataFrame with ILThermo-style mixture data into a list of MixtureRecord objects.

    Each MixtureRecord corresponds to a unique (doi, smi1, smi2) tuple.
    Each MixtureDatum groups a measurement under constant (T, P, units, xtype).
    """
    required_columns = {
        "doi",
        "smi1",
        "name1",
        "smi2",
        "name2",
        "property",
        "value",
        "temperature",
        "temperature_unit",
        "pressure",
        "pressure_unit",
        "x1",
        "xtype",
        "unit",
    }
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Normalize property names
    df["property"] = df["property"].str.strip().str.lower()
    df["property"] = df["property"].replace(PROPERTY_MAP)

    records = []

    # Group by unique chemical systems
    group_cols = ["doi", "smi1", "name1", "smi2", "name2"]
    for (doi, smi1, name1, smi2, name2), group_df in df.groupby(group_cols):
        mixture_data = []

        # Group by measurement condition
        for (
            prop,
            unit,
            T,
            T_unit,
            P,
            P_unit,
            xtype,
        ), meas_df in group_df.groupby(
            [
                "property",
                "unit",
                "temperature",
                "temperature_unit",
                "pressure",
                "pressure_unit",
                "xtype",
            ]
        ):
            datum = MixtureDatum(
                measurement=prop,
                units=unit,
                temperature=TemperatureMeasurement(value=T, unit=T_unit),
                pressure=PressureMeasurement(value=P, unit=P_unit),
                xtype=xtype,
                x1=list(meas_df["x1"]),
                values=list(meas_df["value"]),
            )
            mixture_data.append(datum)

        yield MixtureRecord(
            name1=name1,
            smi1=smi1,
            name2=name2,
            smi2=smi2,
            doi=doi,
            mixture_data=mixture_data,
            pure_compound_data=None,  # You can extend this if you want to infer pure data later
        )


def retrieve_mixture_records(properties: list[str], n_compounds: int = 2):
    dfs = []
    for property in properties:
        logging.info(f"Searching for {property}")
        df: pd.DataFrame = ilt.Search(prop=property, n_compounds=n_compounds)
        df = df[df["num_phases"] == 1]
        df = df[df["phases"] == "Liquid"]
        for _, row in tqdm(df.iterrows(), total=len(df)):
            try:
                if (entry_df := extract_entry(row["id"], property)) is not None:
                    entry_df["ilthermo_id"] = row["id"]
                    dfs.append(entry_df)
            except Exception as e:
                logging.warning("Failed to extract entry for {}: {}", property, e)

    df_data = pd.concat(dfs, ignore_index=True)
    yield from df_to_mixture_records(df_data)
