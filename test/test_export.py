import pytest
from .utils import get_data_file
import pandas as pd
from excess_density.data_model import MixtureRecord
from excess_density.export import as_wide_table

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)


@pytest.fixture()
def mixture_record():
    file = get_data_file()
    return MixtureRecord.parse_jsonfile(file)


def test_wide(mixture_record):
    df = as_wide_table(mixture_record)
    print(df)
    assert "x1" in df.columns
    assert f"temperature [K]" in df.columns
