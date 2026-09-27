from pathlib import Path

SCIENTIFIC_ROOT = Path(__file__).parent

SUBDOMAINS = [
    d.name for d in SCIENTIFIC_ROOT.iterdir()
    if d.is_dir() and not d.name.startswith((".", "_"))
]

__all__ = ["SCIENTIFIC_ROOT", "SUBDOMAINS"]