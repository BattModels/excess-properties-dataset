from numpy import ma
import pandas as pd

from excess_density.units import get_preferred_unit, get_preferred_unit_name, ureg
from .data_model import MixtureRecord


def linear_mixing(x1, y1, y2):
    return y2 + x1 * (y1 - y2)


def mixture_records_df(files):
    dfs = []
    for file in files:
        m = MixtureRecord.parse_jsonfile(file)
        dfs.append(as_wide_table(m))

    return pd.concat(dfs, ignore_index=True)


def as_wide_table(m: MixtureRecord, units_map=None):
    meta = m.metadata
    df = pd.DataFrame.from_records(m.as_records(units_map=units_map))
    df_wide = df.pivot_table(
        index=["x1", "temperature"], columns="measurement", values="value"
    )
    measurement_types = [
        "density",
        "excess density",
        "molar enthalpy",
        "excess molar enthalpy",
        "excess molar volume",
    ]
    df_wide = df_wide.reindex(
        index=df_wide.index, columns=measurement_types
    ).reset_index()

    # Create Density Measurement Lookup
    density_map = (
        df.loc[(df.measurement == "density")]
        .set_index(["temperature", "x1"])[["value", "measurement_units"]]
        .sort_index()
    )
    temperature_unit = df["temperature_units"].iloc[0]
    density_unit = get_preferred_unit("density", units_map)

    # Check that units are sane
    assert ureg.Unit(density_unit).dimensionality == ureg.Unit("g/cm^3").dimensionality
    assert ureg.Unit(temperature_unit).dimensionality == ureg.Unit("K").dimensionality

    # Check that all rows have the same units
    assert (df.groupby("measurement")["measurement_units"].nunique() == 1).all().all()
    assert df["temperature_units"].nunique() == 1

    def _get_density(T, x1):
        if (T.magnitude, x1) in density_map.index:
            return density_map.loc[(T.magnitude, x1), "value"].mean().item()

        return m.get_pure_density(T, density_unit).get(
            "density1" if x1 == 1 else "density2", None
        )

    # Fill in pure component density values
    def fill_pure_density(row):
        T = ureg.Quantity(row["temperature"], temperature_unit)
        row["density1"] = _get_density(T, 1.0)
        row["density2"] = _get_density(T, 0.0)

        return row

    df_wide = df_wide.apply(fill_pure_density, axis=1)

    # Compute mixture molecular weight and ideal density
    df_wide["mw_mix"] = linear_mixing(
        df_wide["x1"], meta["molecular_mass1"], meta["molecular_mass2"]
    )
    df_wide["ideal density"] = linear_mixing(
        df_wide["x1"], df_wide["density1"], df_wide["density2"]
    )

    # Row-wise computation
    def compute_row(row):
        # Handle case: only excess molar volume provided
        if pd.isna(row.get("density")) and not pd.isna(row.get("excess molar volume")):
            # Compute pure molar volumes (cm3/mol)
            V1 = meta["molecular_mass1"] / row["density1"]
            V2 = meta["molecular_mass2"] / row["density2"]
            V_id = linear_mixing(row["x1"], V1, V2)
            V_mix = V_id + row["excess molar volume"]
            # Compute mixture density (g/cm3)
            row["density"] = row["mw_mix"] / V_mix

        # Compute density if still missing via excess density
        if pd.isna(row.get("density")) and not pd.isna(row.get("excess density")):
            row["density"] = row["ideal density"] + row["excess density"]

        # Compute excess density if missing
        if pd.isna(row.get("excess density")) and not pd.isna(row.get("density")):
            row["excess density"] = row["density"] - row["ideal density"]

        # Compute molar volumes
        row["molar volume"] = row["mw_mix"] / row["density"]
        mv1 = meta["molecular_mass1"] / row["density1"]
        mv2 = meta["molecular_mass2"] / row["density2"]
        row["ideal molar volume"] = linear_mixing(row["x1"], mv1, mv2)

        if pd.isna(row.get("excess molar volume")):
            row["excess molar volume"] = row["molar volume"] - row["ideal molar volume"]

        return row

    df_wide = df_wide.apply(compute_row, axis=1)

    # Rename computed columns to include units
    rename_map = {
        "temperature": f"temperature [{get_preferred_unit_name('temperature', units_map)}]",
        "density1": f"density1 [{get_preferred_unit_name('density', units_map)}]",
        "density2": f"density2 [{get_preferred_unit_name('density', units_map)}]",
        "ideal density": f"ideal density [{get_preferred_unit_name('density', units_map)}]",
    }
    for meas in [*measurement_types, "molar volume", "excess molar volume"]:
        if meas in df_wide.columns:
            unit = ureg.Unit(get_preferred_unit(meas, units_map))
            rename_map[meas] = f"{meas} [{unit}]"

    # Fill in metadata
    meta_cols = [
        "doi",
        "name1",
        "name2",
        "smi1",
        "smi2",
        "molecular_mass1",
        "molecular_mass2",
    ]
    for col in meta_cols:
        df_wide[col] = meta[col]

    df_wide = (
        df_wide[[*meta_cols, "x1", *rename_map.keys()]]
        .rename(columns=rename_map)
        .reset_index(drop=True)
    )

    return df_wide
