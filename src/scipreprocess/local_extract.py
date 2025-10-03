from __future__ import annotations

import re
from typing import Any

try:
    from nameparser import HumanName  # type: ignore
except Exception:
    HumanName = None  # type: ignore


DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)
ARXIV_RE = re.compile(r"arXiv:\s*\d{4}\.\d{4,5}(v\d+)?", re.IGNORECASE)
ISSN_RE = re.compile(r"\b\d{4}-\d{3}[\dX]\b", re.IGNORECASE)
ISBN_RE = re.compile(r"\b97[89][- ]?\d{1,5}[- ]?\d{1,7}[- ]?\d{1,7}[- ]?[\dX]\b")
PMID_RE = re.compile(r"PMID:\s*(\d+)", re.IGNORECASE)
PMCID_RE = re.compile(r"PMCID:\s*(PMC\d+)", re.IGNORECASE)
EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
ORCID_RE = re.compile(r"\b\d{4}-\d{4}-\d{4}-\d{3}[\dX]\b")


def parse_toc_lines(text: str) -> list[dict[str, Any]]:
    items: list[dict[str, str | None]] = []
    for line in (raw_line.strip() for raw_line in text.splitlines() if raw_line.strip()):
        # Remove dot leaders
        line = re.sub(r"\s*\.{2,}\s*", " ", line)
        m = re.match(r"^(?P<id>(\d+)(?:\.(\d+))*)\s+(?P<name>.+?)\s+(?P<page>\d+)$", line)
        if m:
            ident = m.group("id")
            parent = ident.rsplit(".", 1)[0] if "." in ident else None
            items.append(
                {
                    "id": ident,
                    "parent_id": parent,
                    "name": m.group("name").strip(),
                    "page": m.group("page"),
                }
            )
            continue
        # fallback: no numeric id
        m2 = re.match(r"^(?P<name>.+?)\s+(?P<page>\d+)$", line)
        if m2:
            items.append(
                {
                    "id": None,
                    "parent_id": None,
                    "name": m2.group("name").strip(),
                    "page": m2.group("page"),
                }
            )
    return items


def parse_list_items(text: str, kind: str) -> list[dict[str, Any]]:
    out: list[dict[str, str | int]] = []
    for line in (raw_line.strip() for raw_line in text.splitlines() if raw_line.strip()):
        line = re.sub(r"\s*\.{2,}\s*", " ", line)
        # Match patterns like "3.1 Title .... 27" or "1 Title 12"
        m = re.match(r"^(?P<num>[A-Za-z0-9_.-]+)\s+(?P<title>.+?)\s+(?P<page>\d+)$", line)
        if not m:
            continue
        if kind == "figures":
            out.append(
                {
                    "figure_number": m.group("num"),
                    "title": m.group("title").strip(),
                    "page": int(m.group("page")),
                }
            )
        elif kind == "tables":
            out.append(
                {
                    "table_number": m.group("num"),
                    "title": m.group("title").strip(),
                    "page": int(m.group("page")),
                }
            )
        else:
            out.append(
                {
                    "number": m.group("num"),
                    "title": m.group("title").strip(),
                    "page": int(m.group("page")),
                }
            )
    return out


def _is_toc_like(text: str) -> bool:
    lines = [
        re.sub(r"\s*\.{2,}\s*", " ", raw_line.strip())
        for raw_line in text.splitlines()
        if raw_line.strip()
    ]
    match_count = 0
    for toc_line in lines:
        if re.match(r"^(\d+(?:\.\d+)*)\s+.+\s+\d+$", toc_line) or re.match(r"^.+\s+\d+$", toc_line):
            match_count += 1
    return match_count >= 5


def parse_term_defs(text: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for line in (raw_line.strip() for raw_line in text.splitlines() if raw_line.strip()):
        m = re.match(r"^(?P<term>[^:–-]+)\s*[:–-]\s*(?P<def>.+)$", line)
        if m:
            out.append({"term": m.group("term").strip(), "definition": m.group("def").strip()})
    return out


def extract_index_sections(
    sections: list[dict[str, Any]], text_pages: list[str]
) -> tuple[dict[str, Any], set[int]]:
    index: dict[str, list[dict[str, Any]] | None] = {
        "toc_structured": None,
        "list_of_figures": None,
        "list_of_tables": None,
        "list_of_algorithms": None,
        "list_of_abbreviations": None,
        "list_of_symbols": None,
        "glossary": None,
    }
    consumed: set[int] = set()
    for i, s in enumerate(sections):
        h = s.get("heading", "").strip().lower()
        t = s.get("text", "")
        if h in ("table of contents", "contents", "toc"):
            items = parse_toc_lines(t)
            index["toc_structured"] = items if items else []
            consumed.add(i)
            continue
        if h.startswith("list of figures"):
            items = parse_list_items(t, "figures")
            index["list_of_figures"] = items if items else []
            consumed.add(i)
            continue
        if h.startswith("list of tables"):
            items = parse_list_items(t, "tables")
            index["list_of_tables"] = items if items else []
            consumed.add(i)
            continue
        if h.startswith("list of algorithms"):
            items = parse_list_items(t, "algorithms")
            index["list_of_algorithms"] = items if items else []
            consumed.add(i)
            continue
        if h in ("list of abbreviations", "abbreviations", "acronyms"):
            items = parse_term_defs(t)
            index["list_of_abbreviations"] = items if items else []
            consumed.add(i)
            continue
        if h in ("list of symbols", "nomenclature"):
            items = parse_term_defs(t)
            index["list_of_symbols"] = items if items else []
            consumed.add(i)
            continue
        if h == "glossary":
            items = parse_term_defs(t)
            index["glossary"] = items if items else []
            consumed.add(i)
            continue
    # Remove None entries
    index = {k: v for k, v in index.items() if v}
    return index, consumed


def extract_identifiers(text_pages: list[str]) -> dict[str, str]:
    text = "\n".join(text_pages)
    ids: dict[str, str] = {}
    doi = DOI_RE.search(text)
    if doi:
        ids["doi"] = doi.group(0).strip()
    arxiv = ARXIV_RE.search(text)
    if arxiv:
        ids["arxiv"] = arxiv.group(0).split(":", 1)[-1].strip()
    issn = ISSN_RE.search(text)
    if issn:
        ids["issn"] = issn.group(0)
    isbn = ISBN_RE.search(text)
    if isbn:
        ids["isbn"] = isbn.group(0)
    pmid = PMID_RE.search(text)
    if pmid:
        ids["pmid"] = pmid.group(1)
    pmcid = PMCID_RE.search(text)
    if pmcid:
        ids["pmcid"] = pmcid.group(1)
    return ids


def extract_header_blocks(text_pages: list[str]) -> dict[str, Any]:
    if not text_pages:
        return {}
    first = text_pages[0]
    # Limit scan to header before the first major section heading
    header_end = len(first)
    m_head = re.search(r"\b(Abstract|Introduction)\b", first, re.IGNORECASE)
    if m_head:
        header_end = m_head.start()
    head_text = first[:header_end]
    lines = [raw_line.strip() for raw_line in head_text.splitlines() if raw_line.strip()]
    header: dict[str, Any] = {}

    # Title guess: longest line near top
    if lines:
        title = max(lines[: min(20, len(lines))], key=len)
        header["title"] = title

    # Authors: delegate to strict extractor
    authors = extract_authors_strict(text_pages)
    if authors:
        header["authors"] = authors

    return header


def extract_authors_strict(text_pages: list[str]) -> list[dict[str, Any]]:
    if not text_pages:
        return []
    first = text_pages[0]
    header_end = len(first)
    m_head = re.search(r"\b(Abstract|Introduction)\b", first, re.IGNORECASE)
    if m_head:
        header_end = m_head.start()
    head_text = first[:header_end]
    lines = [raw_line.strip() for raw_line in head_text.splitlines() if raw_line.strip()]

    stop_words = {
        "pages",
        "proceedings",
        "conference",
        "workshop",
        "journal",
        "volume",
        "vol",
        "issue",
        "unified",
        "toolkit",
        "processing",
        "demonstrations",
        "empirical",
        "methods",
        "natural",
        "language",
        "system",
        "demonstration",
        "committee",
        "association",
        "press",
        "university",
        "institute",
    }

    def normalize_candidate(segment: str) -> tuple[str | None, str | None, str | None]:
        seg = re.sub(r"\s+", " ", segment).strip().strip(",;.")
        if not seg or any(ch.isdigit() for ch in seg):
            return None, None, None
        toks = seg.split()
        if not (2 <= len(toks) <= 6):
            return None, None, None
        if any(t.lower().strip(".,;") in stop_words for t in toks):
            return None, None, None
        if HumanName is not None:
            hn = HumanName(seg)
            first = (hn.first or "").strip()
            last = (hn.last or "").strip()
            full = (hn.full_name or seg).strip()
            if not first or not last:
                return None, None, None
            if any(t in stop_words for t in full.lower().split()):
                return None, None, None
            if len(first) < 2 or len(last) < 2:
                return None, None, None
            return first, last, full
        # Fallback capitalization heuristic
        proper = [t.strip(".,") for t in toks if re.match(r"^[A-Z][a-zA-Z'\-]+\.?$", t)]
        if len(proper) < 2:
            return None, None, None
        return proper[0].rstrip("."), proper[-1].rstrip("."), " ".join(proper)

    found: list[dict[str, Any]] = []
    for header_line in lines[:50]:
        if EMAIL_RE.search(header_line) or (
            ("," in header_line or ";" in header_line or " and " in header_line)
            and sum(w.istitle() for w in header_line.split()) >= 2
        ):
            emails = EMAIL_RE.findall(header_line)
            orcids = ORCID_RE.findall(header_line)
            parts = re.split(r",|;|\band\b", header_line)
            for p in (pp.strip() for pp in parts if pp and pp.strip()):
                g, f, full = normalize_candidate(p)
                if g and f:
                    found.append(
                        {
                            "full": full,
                            "email": emails[0] if emails else None,
                            "orcid": orcids[0] if orcids else None,
                            "affiliations": [],
                        }
                    )
        if found and ("," in header_line or ";" in header_line or " and " in header_line):
            break

    # Fallback: scan for contiguous name-like spans when no delimiters are present
    if not found:
        name_span_re = re.compile(r"\b([A-Z][a-zA-Z'\.-]+(?:\s+[A-Z][a-zA-Z'\.-]+){1,2})\b")
        for idx, header_line in enumerate(lines[:60], start=1):
            # skip likely title lines (first 4 lines)
            if idx <= 4:
                continue
            # consider only early header region to avoid affiliations block
            if idx > 20:
                break
            # skip affiliation-heavy lines
            low = header_line.lower()
            if any(
                w in low
                for w in (
                    "university",
                    "institute",
                    "department",
                    "school",
                    "college",
                    "press",
                    "association",
                )
            ):
                continue
            # strip trailing markers (greek letters/symbols) attached to tokens
            cleaned = re.sub(r"([A-Za-z][a-zA-Z'\.-]+)[^\sA-Za-z]", r"\1", header_line)
            for m in name_span_re.finditer(cleaned):
                cand = m.group(1).strip()
                g, f, full = normalize_candidate(cand)
                if g and f:
                    found.append(
                        {
                            "full": full,
                            "email": None,
                            "orcid": None,
                            "affiliations": [],
                        }
                    )
            if len(found) >= 2:
                break

    # Deduplicate by full name
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for a in found:
        k = a["full"].lower()
        if k in seen:
            continue
        seen.add(k)
        out.append(a)
    return out


def extract_keywords(sections: list[dict[str, Any]], text_pages: list[str]) -> list[dict[str, str]]:
    kws: list[dict[str, str]] = []
    for s in sections:
        if s["heading"].lower().startswith("keywords"):
            terms = re.split(r"[;,]", s["text"]) or []
            kws.extend({"term": t.strip(), "source": "author"} for t in terms if t.strip())
            break
    if not kws and text_pages:
        m = re.search(r"^\s*Keywords\s*[:]?\s*(.+)$", text_pages[0], re.IGNORECASE | re.MULTILINE)
        if m:
            terms = re.split(r"[;,]", m.group(1))
            kws.extend({"term": t.strip(), "source": "author"} for t in terms if t.strip())
    return kws


def extract_venue_info(text_pages: list[str]) -> dict[str, Any]:
    text = "\n".join(text_pages[:2])
    out: dict[str, Any] = {}
    conf = re.search(r"In Proceedings of the\s+(.+?)\.?\s", text, re.IGNORECASE)
    if conf:
        out["conference"] = {"name": conf.group(1).strip()}
    journal = re.search(r"Journal of\s+([A-Z][A-Za-z &-]+)", text)
    if journal:
        out["journal"] = {"title": journal.group(1).strip()}
    vol_issue = re.search(r"(vol\.?\s*\d+).*?(no\.?\s*\d+)", text, re.IGNORECASE)
    if vol_issue:
        j = out.get("journal", {})
        j.update({"volume": vol_issue.group(1), "issue": vol_issue.group(2)})
        out["journal"] = j
    return out


def extract_ack_foot_append(
    sections: list[dict[str, Any]], text_pages: list[str]
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    # Simple mapping section to first matching page
    def find_page(text: str) -> str | None:
        for i, pg in enumerate(text_pages, 1):
            if text[:100] and text[:100] in pg:
                return str(i)
        return None

    acks = {}
    footnotes: list[dict[str, Any]] = []
    appx: list[dict[str, Any]] = []

    for s in sections:
        h = s["heading"].lower()
        if "acknowled" in h:
            acks = {"text": s["text"], "page_span": [find_page(s["text"]), None]}
        if h.startswith("appendix") or "appendix" in h:
            appx.append(
                {
                    "heading": s["heading"],
                    "text": s["text"],
                    "page_span": [find_page(s["text"]), None],
                }
            )

    # Footnotes heuristic: lines that start with a small number + space at bottom of pages
    for idx, pg in enumerate(text_pages, 1):
        for line in pg.splitlines()[-20:]:
            if re.match(r"^\s*\d+\s+.+", line) and len(line) < 200:
                footnotes.append({"id": line.split()[0], "text": line.strip(), "page": str(idx)})

    return acks, footnotes, appx


def enrich_equations(
    equations: list[dict[str, Any]], text_pages: list[str]
) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for eq in equations:
        page = eq.get("page")
        typ = "display"
        tex = None
        if page and isinstance(page, int) and 1 <= page <= len(text_pages):
            pg_text = text_pages[page - 1]
            m = re.search(r"\$\$(.+?)\$\$|\\\[(.+?)\\\]", pg_text, re.DOTALL)
            if m:
                tex = (m.group(1) or m.group(2) or "").strip()
        new_eq = {"type": typ, "number": eq.get("number"), "tex": tex, "mathml": None, "page": page}
        enriched.append(new_eq)
    return enriched
