import pandas as pd

from pint import Quantity
from excess_density.units import get_preferred_unit, get_preferred_unit_name, ureg
from .data_model import MixtureRecord


def linear_mixing(x1, y1, y2):
    return y2 + x1 * (y1 - y2)


def compute_excess_property(x1, y1, y2, y_mix):
    y_id = linear_mixing(x1, y1, y2)
    return y_mix - y_id


def compute_total_property(x1, y1, y2, y_excess):
    y_id = linear_mixing(x1, y1, y2)
    return y_id + y_excess


def mixture_records_df(files):
    dfs = []
    for file in files:
        m = MixtureRecord.parse_jsonfile(file)
        dfs.append(as_wide_table(m))
    return pd.concat(dfs, ignore_index=True)


def as_wide_table(
    m: MixtureRecord, units_map=None, temperature_unit="K", pressure_unit="MPa"
):
    meta = m.metadata
    df = pd.DataFrame.from_records(m.as_records(units_map=units_map))
    df_wide = df.pivot_table(
        index=["x1", "temperature", "pressure"], columns="measurement", values="value"
    )

    all_meas = set(df["measurement"])
    known_excess = {m for m in all_meas if m.startswith("excess ")}
    base_props = {m for m in all_meas if not m.startswith("excess ")}
    base_props |= {m.removeprefix("excess ") for m in known_excess}
    known_excess |= {f"excess {m}" for m in base_props}

    all_required = base_props | known_excess | {"molar volume", "excess molar volume"}
    df_wide = df_wide.reindex(
        index=df_wide.index, columns=sorted(all_required)
    ).reset_index()

    # Create base property lookup maps
    base_map: dict[str, pd.Series] = {}
    for meas in base_props:
        sub = df[(df.measurement == meas)]
        if sub.empty:
            continue
        # build a Series indexed by (T, P, x1)
        base_map[meas] = sub.set_index(["temperature", "pressure", "x1"])[
            "value"
        ].sort_index()

    assert df["temperature_units"].nunique() == 1

    def _get_base_value(meas: str, T: Quantity, P: Quantity, x1: float) -> float | None:
        """Look up the pure‐compound property at exactly (T, P, x1),
        or return None if not measured."""
        key = (T.magnitude, P.to(pressure_unit).magnitude, x1)
        try:
            val = base_map[meas].loc[key]
        except (KeyError, TypeError):
            return None
        # if there happen to be duplicates, pick the first
        if isinstance(val, pd.Series):
            return float(val.iloc[0])
        return float(val)

    def fill_pure_density(row):
        T = ureg.Quantity(row["temperature"], temperature_unit)
        row["density1"] = m.get_pure_density(
            T, get_preferred_unit("density", units_map)
        )["density1"]
        row["density2"] = m.get_pure_density(
            T, get_preferred_unit("density", units_map)
        )["density2"]

        # If possible use the value from measurements
        Tq = ureg.Quantity(row["temperature"], temperature_unit)
        Pq = ureg.Quantity(row["pressure"], pressure_unit)
        row["density1"] = _get_base_value("density", Tq, Pq, 1.0) or row["density1"]
        row["density2"] = _get_base_value("density", Tq, Pq, 0.0) or row["density2"]

        return row

    df_wide = df_wide.apply(fill_pure_density, axis=1)
    df_wide["mw_mix"] = linear_mixing(
        df_wide["x1"], meta["molecular_mass1"], meta["molecular_mass2"]
    )
    df_wide["ideal density"] = linear_mixing(
        df_wide["x1"], df_wide["density1"], df_wide["density2"]
    )

    def compute_row(row):
        for prop in base_props:
            Tq = ureg.Quantity(row["temperature"], temperature_unit)
            Pq = ureg.Quantity(row["pressure"], pressure_unit)
            y1 = _get_base_value(prop, Tq, Pq, 1.0)
            y2 = _get_base_value(prop, Tq, Pq, 0.0)

            if y1 is not None and y2 is not None:
                if pd.isna(row.get(prop)) and not pd.isna(row.get(f"excess {prop}")):
                    row[prop] = compute_total_property(
                        row["x1"], y1, y2, row[f"excess {prop}"]
                    )
                elif pd.isna(row.get(f"excess {prop}")) and not pd.isna(row.get(prop)):
                    row[f"excess {prop}"] = compute_excess_property(
                        row["x1"], y1, y2, row[prop]
                    )

        if pd.isna(row.get("density")) and not pd.isna(row.get("excess molar volume")):
            V1 = meta["molecular_mass1"] / row["density1"] if row["density1"] else None
            V2 = meta["molecular_mass2"] / row["density2"] if row["density2"] else None
            if V1 and V2:
                V_id = linear_mixing(row["x1"], V1, V2)
                V_mix = V_id + row["excess molar volume"]
                row["density"] = row["mw_mix"] / V_mix if V_mix else None

        if pd.isna(row.get("density")) and not pd.isna(row.get("excess density")):
            row["density"] = row["ideal density"] + row["excess density"]

        if pd.isna(row.get("excess density")) and not pd.isna(row.get("density")):
            row["excess density"] = row["density"] - row["ideal density"]

        if row.get("density"):
            row["molar volume"] = row["mw_mix"] / row["density"]
        else:
            row["molar volume"] = None

        mv1 = meta["molecular_mass1"] / row["density1"] if row["density1"] else None
        mv2 = meta["molecular_mass2"] / row["density2"] if row["density2"] else None
        if mv1 is not None and mv2 is not None:
            row["ideal molar volume"] = linear_mixing(row["x1"], mv1, mv2)
            if pd.isna(row.get("excess molar volume")) and row.get("molar volume"):
                row["excess molar volume"] = (
                    row["molar volume"] - row["ideal molar volume"]
                )

        return row

    df_wide = df_wide.apply(compute_row, axis=1)

    rename_map = {
        "temperature": f"temperature [{get_preferred_unit_name('temperature', units_map)}]",
        "pressure": f"pressure [{get_preferred_unit_name('pressure', units_map)}]",
        "density1": f"density1 [{get_preferred_unit_name('density', units_map)}]",
        "density2": f"density2 [{get_preferred_unit_name('density', units_map)}]",
        "ideal density": f"ideal density [{get_preferred_unit_name('density', units_map)}]",
    }
    for meas in sorted(df_wide.columns.difference(rename_map)):
        if meas in all_required:
            try:
                unit = get_preferred_unit_name(meas.strip())
                rename_map[meas] = f"{meas} [{unit}]"
            except Exception:
                continue

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
