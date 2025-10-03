"""Lightweight entity linking utilities (normalization/validation only)."""

from __future__ import annotations

import re
from typing import Any

_DOI_RE = re.compile(r"^10\.\d{4,9}/[-._;()/:A-Z0-9]+$", re.IGNORECASE)
_ORCID_RE = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")
_ISSN_RE = re.compile(r"^\d{4}-\d{3}[\dX]$", re.IGNORECASE)
_ROR_RE = re.compile(r"^https?://ror\.org/[0-9a-z]{9}$", re.IGNORECASE)


def _norm(s: str | None) -> str | None:
    if not s:
        return None
    return s.strip()


def normalize_doi(doi: str | None) -> str | None:
    doi = _norm(doi)
    if not doi:
        return None
    doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "").strip()
    return doi if _DOI_RE.match(doi) else None


def normalize_orcid(orcid: str | None) -> str | None:
    orcid = _norm(orcid)
    if not orcid:
        return None
    orcid = orcid.replace("https://orcid.org/", "").replace("http://orcid.org/", "").strip()
    return orcid if _ORCID_RE.match(orcid) else None


def normalize_issn(issn: str | None) -> str | None:
    issn = _norm(issn)
    if not issn:
        return None
    return issn.upper() if _ISSN_RE.match(issn) else None


def normalize_ror(ror: str | None) -> str | None:
    ror = _norm(ror)
    if not ror:
        return None
    if ror and not ror.startswith("http"):
        ror = f"https://ror.org/{ror}"
    return ror if _ROR_RE.match(ror) else None


def build_entity_linking(doc_json: dict[str, Any]) -> dict[str, Any]:
    """Populate entity_linking map with normalized ids and simple confidences.

    No external API calls; format/regex checks only.
    """
    md = doc_json.get("metadata", {})
    identifiers = md.get("identifiers", {})

    linking: dict[str, Any] = {"document": {}, "authors": [], "affiliations": [], "venues": {}}

    # Document ids
    doi = normalize_doi(identifiers.get("doi"))
    if doi:
        linking["document"]["doi"] = {"id": doi, "confidence": 0.9}
    for k in ("issn", "eissn"):
        val = normalize_issn(identifiers.get(k))
        if val:
            linking["venues"][k] = {"id": val, "confidence": 0.8}

    # Authors
    for a in md.get("authors", []) or []:
        entry: dict[str, Any] = {
            "name": a.get("full") or f"{a.get('given','')} {a.get('family','')}".strip()
        }
        orcid = normalize_orcid(a.get("orcid"))
        if orcid:
            entry["orcid"] = {"id": orcid, "confidence": 0.95}
        linking["authors"].append(entry)

    # Affiliations
    aff_norm = []
    for a in md.get("authors") or []:
        for aff in a.get("affiliations", []) or []:
            ror = normalize_ror(aff.get("ror")) if isinstance(aff, dict) else None
            aff_entry: dict[str, Any] = {
                "name": (aff.get("name") if isinstance(aff, dict) else None)
            }
            if ror:
                aff_entry["ror"] = {"id": ror, "confidence": 0.8}
            aff_norm.append(aff_entry)
    if aff_norm:
        linking["affiliations"] = aff_norm

    return linking
