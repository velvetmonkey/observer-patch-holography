#!/usr/bin/env python3
"""
PDG Particle Data Downloader
Fetches particle masses from the PDG database via the official pdg Python package.
Exports to CSV and JSON.

Install: pip install pdg pandas
"""

import json
import logging
import pdg
import pandas as pd
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "pdg_data"
OUTPUT_DIR.mkdir(exist_ok=True)
LOGGER = logging.getLogger(__name__)

# (PDG name or mcid, label, fallback PDG property ID, unit of fallback)
# Some particles (light quarks, pi0) need direct property lookup because
# the .mass attribute fails in the 2025 API.
PARTICLES = [
    # Quarks
    ("u", "up quark", "Q002M", "MeV"),
    ("d", "down quark", "Q001M", "MeV"),
    ("s", "strange quark", "Q003M", "MeV"),
    ("c", "charm quark", "Q004M", "GeV"),
    ("b", "bottom quark", "Q005M", "GeV"),
    ("t", "top quark", None, "GeV"),
    # Leptons
    ("e-", "electron", None, "GeV"),
    ("mu-", "muon", None, "GeV"),
    ("tau-", "tau", None, "GeV"),
    # Gauge bosons
    ("W+", "W boson", None, "GeV"),
    ("Z0", "Z boson", None, "GeV"),
    # Higgs
    ("H", "Higgs boson", None, "GeV"),
    # Hadrons
    ("p", "proton", None, "GeV"),
    ("n", "neutron", None, "GeV"),
    ("pi+", "pion (charged)", None, "GeV"),
    ("pi0", "pion (neutral)", "S009M", "MeV"),
    ("K+", "kaon (charged)", None, "GeV"),
    ("K0", "kaon (neutral)", None, "GeV"),
    (3122, "Lambda", None, "GeV"),
]


def fetch_mass(api, pdg_id, fallback_prop, unit):
    """Get mass in GeV and uncertainties for a particle."""
    # Try standard particle lookup first
    try:
        if isinstance(pdg_id, int):
            p = api.get_particle_by_mcid(pdg_id)
        else:
            p = api.get_particle_by_name(pdg_id)

        mass_property = p.best(p.masses(), f"{label_for(pdg_id)} mass")
        summary = mass_property.best_summary()
        if summary is not None and not summary.is_limit:
            # Summary values and errors are expressed in summary.units (often
            # MeV or atomic mass units). Convert all three through the PDG
            # package instead of pairing p.mass (GeV) with raw summary errors.
            return (
                summary.get_value("GeV"),
                summary.get_error_positive("GeV"),
                summary.get_error_negative("GeV"),
            )
    except Exception:
        LOGGER.exception("Standard PDG mass lookup failed for %r", pdg_id)

    # Fallback: direct property ID lookup (light quarks, pi0)
    if fallback_prop is not None:
        try:
            item = api.get(fallback_prop)
            s = item.best_summary()
            if s is not None and s.value is not None:
                return (
                    s.get_value("GeV"),
                    s.get_error_positive("GeV"),
                    s.get_error_negative("GeV"),
                )
        except Exception:
            LOGGER.exception("Fallback PDG lookup failed for %s", fallback_prop)

    return None, None, None


def label_for(pdg_id):
    """Stable diagnostic label that does not trigger another API lookup."""
    return str(pdg_id)


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    print("Connecting to PDG database...")
    api = pdg.connect()
    print(f"PDG edition: {api.edition}\n")

    rows = []
    for entry in PARTICLES:
        pdg_id, label, fallback_prop, unit = entry
        mass, err_plus, err_minus = fetch_mass(api, pdg_id, fallback_prop, unit)
        if mass is not None:
            print(f"  {label:25s}  {mass:.10g} GeV  (+{err_plus} / {err_minus})")
        else:
            print(f"  {label:25s}  no mass data")
        rows.append({
            "particle": label,
            "pdg_name": str(pdg_id),
            "mass_GeV": mass,
            "err_plus_GeV": err_plus,
            "err_minus_GeV": err_minus,
        })

    df = pd.DataFrame(rows)

    csv_path = OUTPUT_DIR / "particle_masses.csv"
    df.to_csv(csv_path, index=False)
    print(f"\nSaved CSV -> {csv_path}")

    json_path = OUTPUT_DIR / "particle_masses.json"
    records = df.to_dict(orient="records")
    with open(json_path, "w") as f:
        json.dump(records, f, indent=2)
    print(f"Saved JSON -> {json_path}")

    print(f"\nTotal particles: {len(df)}")
    print(f"With mass data: {df['mass_GeV'].notna().sum()}")


if __name__ == "__main__":
    main()
