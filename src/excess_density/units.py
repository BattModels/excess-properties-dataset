from typing import Annotated
from pint import UnitRegistry
from pydantic import AfterValidator

ureg = UnitRegistry()


def valid_unit(unit: str):
    try:
        ureg.Unit(unit)
    except Exception as e:
        raise ValueError(f"Invalid unit '{unit}': {e}")
    return unit


UnitField = Annotated[str, AfterValidator(valid_unit)]

# Default measurement -> unit mapping
DEFAULT_UNITS: dict[str, UnitField] = {
    "density": "g/cm^3",
    "molar enthalpy": "J/mol",
    "temperature": "K",
    "pressure": "MPa",
    "molar volume": "cm^3/mol",
    "thermal diffusivity": "mm**2/s",
    "viscosity": "mPa*s",
    "speed of sound": "m/s",
    "electrical conductivity": "S/m",
}


def get_preferred_unit(
    measurement: str, units_map: dict[str, str] | None = None
) -> str:
    measurement = measurement.removeprefix("excess").strip()
    if units_map is None:
        return DEFAULT_UNITS[measurement]
    return units_map.get(measurement, DEFAULT_UNITS[measurement])


def get_preferred_unit_name(measurement: str, units_map: dict[str, str] | None = None):
    return str(ureg.Unit(get_preferred_unit(measurement, units_map)))
