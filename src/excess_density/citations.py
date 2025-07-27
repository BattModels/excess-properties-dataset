import requests


def fetch_bibtex_from_doi(doi: str) -> str:
    """Fetch BibTeX entry from a DOI using the CrossRef API."""
    url = f"https://doi.org/{doi}"
    headers = {"Accept": "application/x-bibtex"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text.strip()
    else:
        raise ValueError(
            f"Failed to fetch BibTeX for DOI {doi} (HTTP {response.status_code})"
        )


def generate_bibtex_bibliography(dois: list[str]) -> str:
    """Generate a BibTeX bibliography from a list of DOIs."""
    bib_entries = []
    for doi in dois:
        try:
            bibtex = fetch_bibtex_from_doi(doi)
            bib_entries.append(bibtex)
        except ValueError as e:
            print(e)
    return "\n\n".join(bib_entries)
