import pytest
from excess_density.cli import validate
from .utils import get_data_files


@pytest.mark.parametrize("file", get_data_files())
def test_all_files_pass_validation(file):
    validate(file)
