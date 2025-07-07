import json
import sys
from itertools import chain
from pathlib import Path
from typing import Annotated

import pandas as pd
import pubchempy
import typer
from pydantic import ValidationError
from rdkit import Chem

from .data_model import MixtureRecord
from .export import mixture_records_df

app = typer.Typer()


def _validate_file(file: Path):
    with open(file, "r") as fid:
        data = json.load(fid)
    record = MixtureRecord.val(**data)


def _get_files(path: Path):
    if path.is_dir():
        return chain(path.glob("**/*.jsonc"), path.glob("**/*.json"))
    else:
        return [path]


@app.command()
def validate(path: Path):
    for file in _get_files(path):
        try:
            MixtureRecord.parse_jsonfile(file)
        except ValidationError as e:
            print(file)
            print(e)


@app.command()
def cat(file: Path):
    assert file.is_file()
    print(MixtureRecord.parse_jsonfile(file))


@app.command()
def export(path: Path, output: Path | None = None):
    files = _get_files(path)
    df = mixture_records_df(files)
    df["percent excess molar volume"] = (
        100
        * df["excess molar volume [centimeter ** 3 / mole]"]
        / (
            df["molar volume [centimeter ** 3 / mole]"]
            - df["excess molar volume [centimeter ** 3 / mole]"]
        )
    )

    with pd.option_context("display.max_rows", None, "display.max_columns", None):
        print(df.describe().T)

    df.round(4).to_csv(output or sys.stdout)


def get_smiles(name: str) -> str | None:
    results = pubchempy.get_compounds(name, namespace="name")
    if len(results) == 0:
        return None
    names = results[0].synonyms
    names = names[: (min(len(names), 5))]
    smi = Chem.MolToSmiles(Chem.MolFromInchi(results[0].inchi))
    print(f"Matched {name} to {', '.join(names)} -> {smi}")
    return smi


@app.command()
def add(
    doi: Annotated[str, typer.Option(prompt="DOI")],
    name1: Annotated[str, typer.Option(prompt="Name of Compound 1 (Pure when x=1)")],
    name2: Annotated[str, typer.Option(prompt="Name of Compound 2 (Pure when x=0)")],
):
    doi_path = Path("data", doi.replace("/", "--"))
    doi_path.mkdir(exist_ok=True, parents=True)
    smi1 = get_smiles(name1)
    smi2 = get_smiles(name2)
    record = {
        "name1": name1,
        "name2": name2,
        "smi1": smi1,
        "smi2": smi2,
        "doi": doi,
        "pure_compound_data": {
            smi1: {"density": 0, "temperature": 298.15},
            smi2: {"density": 0, "temperature": 298.15},
        },
        "mixture_data": [
            {
                "measurement": "density",
                "units": "g/cm^3",
                "temperature": 298.15,
                "xtype": "mole fraction",
                "x1": [],
                "values": [],
            }
        ],
    }
    output = Path(doi_path, f"{smi1}--{smi2}.json")
    _ = output.write_text(json.dumps(record, indent=2))
    print("Wrote template file to: ", output)
