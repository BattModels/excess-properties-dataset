from pathlib import Path


def get_data_files():
    data_dir = Path(__file__).parent.parent.joinpath("data")
    yield from data_dir.glob("**/*.json")
    yield from data_dir.glob("**/*.jsonc")


def get_data_file():
    return next(get_data_files())
