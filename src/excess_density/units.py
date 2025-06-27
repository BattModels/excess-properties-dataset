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
