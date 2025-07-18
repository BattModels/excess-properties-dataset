import json
import re
import sys
import unicodedata
from itertools import chain
from pathlib import Path
from typing import Annotated

import pandas as pd
from pandas.core.frame import rec_array_to_mgr
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
    multiple_temp: bool = False,
):
    doi_path = Path("data", doi.replace("/", "--"))
    doi_path.mkdir(exist_ok=True, parents=True)
    name1 = re.sub(r"\s+", " ", name1).strip()
    name2 = re.sub(r"\s+", " ", name2).strip()
    smi1 = get_smiles(name1) or input("smi1:")
    smi2 = get_smiles(name2) or input("smi2:")

    if multiple_temp:
        pure_template = {
            "density": {"values": [0], "temperature": [298.15], "units": "g/cm^3"}
        }
    else:
        pure_template = {"density": 0, "temperature": 298.15}

    record = {
        "name1": name1,
        "name2": name2,
        "smi1": smi1,
        "smi2": smi2,
        "doi": doi,
        "pure_compound_data": {
            smi1: pure_template,
            smi2: pure_template,
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

    # Clean up smiles for file system
    smi1 = smi1.replace("/", "--").replace("\\", "---")
    smi2 = smi2.replace("/", "--").replace("\\", "---")
    output = Path(doi_path, f"{smi1}--{smi2}.json")
    if output.exists():
        raise FileExistsError(output)

    _ = output.write_text(json.dumps(record, indent=2))
    print("Wrote template file to: ", output)


def parse_round_robin_columns(text: str, names: list[str]) -> dict[str, list[float]]:
    # Match all floats, including ones with Unicode minus

    pattern = re.compile(r"[+-]?\d+(?:\.\d+ {0,2}\d+|\.\d+| ?\d+)?")

    text = (
        unicodedata.normalize("NFKC", text)
        .replace("–", "-")  # EN DASH (U+2013)
        .replace("—", "-")  # EM DASH (U+2014)
        .replace("‒", "-")  # FIGURE DASH (U+2012)
    )
    lines = text.strip().splitlines()

    # Parse all lines into rows of floats
    rows = [
        [float(token.replace(" ", "")) for token in pattern.findall(line)]
        for line in text.strip().splitlines()
        if line.strip()
    ]

    n_fields = len(names)
    result = {name: [] for name in names}

    for col in range(len(rows[0])):
        field = names[col % n_fields]
        for row in rows:
            if col < len(row):
                result[field].append(row[col])

    return result


@app.command()
def parse_data(columns: list[str]):
    raw_text = sys.stdin.read()
    result = parse_round_robin_columns(raw_text, columns)
    for k, v in result.items():
        print(f"{k}:", json.dumps(v))
