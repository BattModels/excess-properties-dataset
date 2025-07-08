import json
from pathlib import Path
from pydantic import BaseModel, Field, model_validator
from typing import Literal, Any
from collections.abc import Sequence
from .units import UnitField, get_preferred_unit, ureg
from pint import Quantity
from .chem import SMILES, inchi_key, molecular_weight
from .utils import parse_jsonc


class Measurement(BaseModel):
    value: float
    unit: UnitField

    @property
    def quantity(self):
        return ureg.Quantity(self.value, self.unit)

    @model_validator(mode="before")
    @classmethod
    def coerce_float(cls, data):
        if isinstance(data, (int, float)):
            # Look up default value for the `unit` field
            unit_default = (
                cls.model_fields.get("unit") and cls.model_fields["unit"].default
            )
            if unit_default is None:
                raise ValueError(
                    f"Measurement subclass '{cls.__name__}' must define a default unit."
                )
            return {"value": float(data), "unit": unit_default}
        return data

    def to_units(self, unit: str) -> float:
        return self.quantity.to(unit).magnitude


class TemperatureMeasurement(Measurement):
    unit: UnitField = get_preferred_unit("temperature")


class PressureMeasurement(Measurement):
    unit: str = get_preferred_unit("pressure")


class DensityMeasurement(Measurement):
    unit: str = get_preferred_unit("density")

    @model_validator(mode="after")
    @classmethod
    def check_range(cls, m: "DensityMeasurement"):
        if m.value <= 0:
            raise ValueError("Density must be >0")
        return m


class MixtureDatum(BaseModel):
    measurement: Literal[
        "density",
        "excess density",
        "molar volume",
        "excess molar density",
        "excess molar enthalpy",
        "excess molar volume",
        "molar enthalpy",
    ]
    units: UnitField
    temperature: TemperatureMeasurement

    pressure: PressureMeasurement = Field(
        default_factory=lambda: PressureMeasurement(value=0.1, unit="MPa")
    )
    xtype: Literal["mole fraction"] = "mole fraction"
    x1: Sequence[float]
    values: Sequence[float]

    @model_validator(mode="after")
    @classmethod
    def check_units_with_pint(cls, datum):
        # define the expected dimensionality for each measurement
        expected = {
            "density": ureg("g/cm**3").dimensionality,
            "excess density": ureg("g/cm**3").dimensionality,
            "excess molar density": ureg("mol/cm**3").dimensionality,
            "excess molar enthalpy": ureg("J/mol").dimensionality,
            "excess molar volume": ureg("cm**3/mol").dimensionality,
            "molar volume": ureg("cm**3/mol").dimensionality,
            "molar enthalpy": ureg("J/mol").dimensionality,
        }

        exp_dim = expected[datum.measurement]
        try:
            u = ureg.Unit(datum.units)
        except Exception as e:
            raise ValueError(f"Could not parse units '{datum.units}': {e}")

        if u.dimensionality != exp_dim:
            raise ValueError(
                f"Wrong units for '{datum.measurement}': "
                f"got '{datum.units}' ({u.dimensionality}), "
                f"expected dimensionality {exp_dim}"
            )
        return datum

    @model_validator(mode="after")
    @classmethod
    def check_values_x1_len_match(cls, datum):
        if len(datum.x1) != len(datum.values):
            raise ValueError(
                "Different lengths for x1 and values: %d vs. %d",
                len(datum.x1),
                len(datum.values),
            )
        return datum


class PureCompoundDatum(BaseModel):
    density: list[DensityMeasurement]
    temperature: list[TemperatureMeasurement] | None = None

    @model_validator(mode="before")
    @classmethod
    def lift_scalar_to_vector(cls, data: Any):
        if isinstance(data, dict):
            if "density" in data:
                density = data["density"]
                if isinstance(density, float | int):
                    data["density"] = [DensityMeasurement(value=density)]
                    data["temperature"] = (
                        [TemperatureMeasurement(value=data["temperature"])]
                        if "temperature" in data
                        else None
                    )
                    return data
                elif isinstance(density, dict):
                    data["density"] = [
                        DensityMeasurement(value=v, unit=density.get("units", "g/cm^3"))
                        for v in density["values"]
                    ]
                    data["temperature"] = [
                        TemperatureMeasurement(
                            value=v, unit=density.get("temperature_units", "K")
                        )
                        for v in density["temperature"]
                    ]
                    return data
        raise ValueError(f"Invalid format: {data}")

    def get_temperature_value(self, T: Quantity, units="g/cm^3") -> float | None:
        """Returns the density value closest to the given temperature (exact match)."""
        if self.temperature is None:
            if len(self.density) == 1:
                return self.density[0].to_units(units)
            else:
                return None
        else:
            for t, v in zip(self.temperature, self.density):
                if T == t.quantity:
                    return v.to_units(units)
        return None


class MixtureRecord(BaseModel):
    name1: str
    smi1: SMILES
    name2: str
    smi2: SMILES
    doi: str
    mixture_data: Sequence[MixtureDatum]
    pure_compound_data: dict[str, PureCompoundDatum] | None = None

    @model_validator(mode="after")
    def validate_pure_keys(self) -> "MixtureRecord":
        if self.pure_compound_data:
            allowed_keys = {self.smi1, self.smi2}
            actual_keys = set(self.pure_compound_data.keys())
            if not actual_keys.issubset(allowed_keys):
                raise ValueError(
                    f"Invalid keys in pure_compound_data: {actual_keys - allowed_keys}. "
                    f"Only {allowed_keys} are allowed."
                )
        return self

    @classmethod
    def parse_jsonfile(cls, file: Path):
        if file.suffix == ".jsonc":
            data = parse_jsonc(file.read_text())
        else:
            with open(file, "r") as fid:
                data = json.load(fid)
        return cls(**data)

    def __str__(self) -> str:
        return "\n".join(
            [
                f"{self.name1} ({self.smi1}) -- ({self.name2} ({self.smi2}))",
                f"Meta: {self.metadata}",
                f"Measurement Types: {self.measurment_types}",
                f"Temperature [K]: {self.temperatures()}",
                "Records:",
                *[str(r) for r in self.as_records()],
            ]
        )

    @property
    def measurment_types(self):
        mt = set()
        for m in self.mixture_data:
            mt.add(m.measurement)

        return mt

    def get_pure_density(
        self, temperature: Quantity, units: str = get_preferred_unit("density")
    ):
        if self.pure_compound_data is None:
            return {f"density1": None, f"density2": None}
        else:
            return {
                f"density1": self.pure_compound_data[self.smi1].get_temperature_value(
                    temperature, units
                ),
                f"density2": self.pure_compound_data[self.smi2].get_temperature_value(
                    temperature, units
                ),
            }

    @property
    def metadata(self):
        return {
            "name1": self.name1,
            "smi1": self.smi1,
            "inchi_key1": inchi_key(self.smi1),
            "molecular_mass1": molecular_weight(self.smi1),
            "name2": self.name2,
            "smi2": self.smi2,
            "inchi_key2": inchi_key(self.smi2),
            "molecular_mass2": molecular_weight(self.smi2),
            "doi": self.doi,
        }

    def temperatures(self, unit: str = "K"):
        t = set()
        if self.pure_compound_data is not None:
            for v in self.pure_compound_data.values():
                if v.temperature is not None:
                    t.update([d.to_units(unit) for d in v.temperature])

        for m in self.mixture_data:
            t.add(m.temperature.to_units(unit))

        return t

    def get_measurements(
        self,
        measurement_type: str,
        temperature: Quantity,
        units_map: dict[str, str] | None = None,
    ):
        m_units = get_preferred_unit(measurement_type, units_map)
        for m in self.mixture_data:
            if m.measurement != measurement_type:
                continue
            if m.temperature.quantity != temperature:
                continue
            for x1, value in zip(m.x1, m.values):
                q = ureg.Quantity(value, m.units).to(m_units)
                yield {
                    "measurement": m.measurement,
                    "value": q.magnitude,
                    "measurement_units": str(q.units),
                    "temperature": temperature.magnitude,
                    "temperature_units": str(temperature.units),
                    "xtype": m.xtype,
                    "x1": x1,
                    "x2": 1 - x1,
                }

    def as_records(self, units_map: dict[str, str] | None = None):
        temperature_unit = get_preferred_unit("temperature", units_map)
        for T in self.temperatures(temperature_unit):
            temperature = ureg.Quantity(T, temperature_unit).to(temperature_unit)
            pure_density = self.get_pure_density(temperature)
            for mtype in self.measurment_types:
                for m_record in self.get_measurements(
                    mtype, temperature=temperature, units_map=units_map
                ):
                    yield {
                        **m_record,
                        **pure_density,
                    }
