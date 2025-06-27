from pint import Quantity
from rdkit import Chem
from rdkit.Chem import Descriptors
from typing import Annotated
from pydantic import AfterValidator


def valid_smiles(smiles: str):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError("Faild to parse smiles: %s", smiles)
    return smiles


SMILES = Annotated[str, AfterValidator(valid_smiles)]


def inchi_key(smiles: str) -> str:
    mol = Chem.MolFromSmiles(smiles)
    return Chem.MolToInchiKey(mol)


def molecular_weight(smiles: str) -> float:
    mol = Chem.MolFromSmiles(smiles)
    return Descriptors.MolWt(mol)


def ideal_density(x1: list[float], density: list[Quantity]) -> list[Quantity]:
    frac_density = {x: d for x, d in zip(x1, density)}
    rho1 = frac_density[0.0]
    rho2 = frac_density[1.0]
    rho_delta = rho2 - rho1
    return [rho1 + x * rho_delta for x in x1]


def excess_density(x1: list[float], density: list[Quantity]):
    assert x1 == sorted(x1)
    rho_ideal = ideal_density(x1, density)
    return [d - i for d, i in zip(density, rho_ideal)]
