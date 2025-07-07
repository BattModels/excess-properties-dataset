from excess_density.data_model import TemperatureMeasurement
from excess_density.units import ureg


def test_to_unit():
    m = TemperatureMeasurement(value=25, unit="degC")
    assert ureg.Quantity(25, "degC").to("K").magnitude == 298.15
    assert m.to_units("K") == 298.15
