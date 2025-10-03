"""Document parsers for various scientific document formats."""

from __future__ import annotations

import pathlib
import re
from typing import Any

from .models import ParsedDocument
from .utils import ET, cv2, docx, fitz


def detect_format(file_path: str) -> str:
    """Detect document format from file extension.

    Args:
        file_path: Path to the document.

    Returns:
        Format identifier (pdf, docx, tex, xml, txt).

    Raises:
        ValueError: If format is not supported.
    """
    ext = pathlib.Path(file_path).suffix.lower()
    if ext in {".pdf", ".docx", ".tex", ".xml", ".txt"}:
        return ext[1:]
    raise ValueError(f"Unsupported file format: {file_path}")


def render_pdf_page_to_image(page, dpi: int = 200):
    """Render a PDF page to an image.

    Args:
        page: PyMuPDF page object.
        dpi: Resolution for rendering.

    Returns:
        Numpy array (if OpenCV available) or PyMuPDF pixmap.
    """
    if fitz is None:
        return None

    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)

    if cv2 is None:
        return pix

    import numpy as np

    # Shape is (height, width, channels) with dtype uint8
    img: Any = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
    if pix.n == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    return img


def extract_figures_from_pdf(doc) -> list[dict]:
    """Extract figure captions and positions from PDF.

    Args:
        doc: PyMuPDF document object.

    Returns:
        List of dictionaries with figure information.
    """
    figures = []
    figure_pattern = re.compile(r"(Figure|Fig\.?)\s+(\d+)", re.IGNORECASE)

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")

        # Find figure captions
        for match in figure_pattern.finditer(text):
            start_pos = match.start()
            # Extract caption (next ~200 chars after figure number)
            end_pos = min(start_pos + 300, len(text))
            caption_text = text[start_pos:end_pos]
            # Find end of caption (usually at next newline or period followed by newline)
            caption_end = caption_text.find("\n\n")
            if caption_end > 0:
                caption_text = caption_text[:caption_end]

            figures.append(
                {
                    "type": "figure",
                    "number": match.group(2),
                    "caption": caption_text.strip(),
                    "page": page_num + 1,
                }
            )

    return figures


def extract_tables_from_pdf(doc) -> list[dict]:
    """Extract table captions and positions from PDF.

    Args:
        doc: PyMuPDF document object.

    Returns:
        List of dictionaries with table information.
    """
    tables = []
    table_pattern = re.compile(r"Table\s+(\d+)", re.IGNORECASE)

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")

        # Find table captions
        for match in table_pattern.finditer(text):
            start_pos = match.start()
            end_pos = min(start_pos + 300, len(text))
            caption_text = text[start_pos:end_pos]
            caption_end = caption_text.find("\n\n")
            if caption_end > 0:
                caption_text = caption_text[:caption_end]

            tables.append(
                {
                    "type": "table",
                    "number": match.group(1),
                    "caption": caption_text.strip(),
                    "page": page_num + 1,
                }
            )

    return tables


def extract_equations_from_pdf(doc) -> list[dict]:
    """Extract equation references from PDF.

    Args:
        doc: PyMuPDF document object.

    Returns:
        List of dictionaries with equation information.
    """
    equations = []
    # Match equation patterns like (1), Eq. (1), Equation 1, etc.
    equation_pattern = re.compile(r"(Equation|Eq\.?)\s*[(\[]?(\d+)[)\]]?", re.IGNORECASE)
    numbered_eq_pattern = re.compile(r"\((\d+)\)\s*$", re.MULTILINE)

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")

        # Find explicit equation references
        seen_numbers = set()
        for match in equation_pattern.finditer(text):
            eq_num = match.group(2)
            if eq_num not in seen_numbers:
                equations.append({"type": "equation", "number": eq_num, "page": page_num + 1})
                seen_numbers.add(eq_num)

        # Find numbered equations (lines ending with (1), (2), etc.)
        for match in numbered_eq_pattern.finditer(text):
            eq_num = match.group(1)
            if eq_num not in seen_numbers:
                equations.append({"type": "equation", "number": eq_num, "page": page_num + 1})
                seen_numbers.add(eq_num)

    return equations


def extract_references_from_pdf(doc, text_pages: list[str]) -> list[dict]:
    """Extract references section from PDF.

    Args:
        doc: PyMuPDF document object.
        text_pages: List of text content per page.

    Returns:
        List of dictionaries with reference information.
    """
    references: list[dict[str, str]] = []
    full_text = "\n".join(text_pages)

    # Find References section
    ref_pattern = re.compile(
        r"\n\s*(References|REFERENCES|Bibliography|BIBLIOGRAPHY)\s*\n", re.IGNORECASE
    )
    match = ref_pattern.search(full_text)

    if not match:
        return references

    ref_start = match.end()
    ref_text = full_text[ref_start:]

    # Try to find end of references (common section that follows or end of document)
    end_patterns = [
        r"\n\s*(Appendix|APPENDIX|Acknowledgments|ACKNOWLEDGMENTS)\s*\n",
    ]
    ref_end = len(ref_text)
    for pattern in end_patterns:
        end_match = re.search(pattern, ref_text)
        if end_match:
            ref_end = end_match.start()
            break

    ref_text = ref_text[:ref_end]

    # Split references by common patterns
    # Look for [1], [2] or 1., 2. at start of lines
    ref_items = re.split(r"\n\s*(?:\[(\d+)\]|(\d+)\.)\s+", ref_text)

    current_ref = None
    for i, item in enumerate(ref_items):
        if not item:
            continue

        # Check if this is a reference number
        if item.isdigit() and i + 1 < len(ref_items) and ref_items[i + 1] is not None:
            if current_ref:
                references.append(current_ref)
            current_ref = {"number": item, "text": ref_items[i + 1].strip()}

    if current_ref:
        references.append(current_ref)

    # If we didn't find numbered references, try line-by-line
    if not references:
        lines = [line.strip() for line in ref_text.split("\n") if line.strip()]
        for i, line in enumerate(lines, 1):
            if len(line) > 20:  # Skip very short lines
                references.append({"number": str(i), "text": line})

    return references


def extract_text_from_pdf(
    pdf_path: str, use_ocr: bool = False, use_layout: bool = False
) -> ParsedDocument:
    """Extract text from a PDF document.

    Args:
        pdf_path: Path to the PDF file.
        use_ocr: Whether OCR might be needed.
        use_layout: Whether layout analysis might be needed.

    Returns:
        ParsedDocument with extracted text and metadata.

    Raises:
        RuntimeError: If PyMuPDF is not available.
    """
    if fitz is None:
        raise RuntimeError("PyMuPDF not available")

    doc = fitz.open(pdf_path)
    text_pages: list[str] = []
    images: list[Any] = []
    total_text_len = 0

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        text = page.get_text("text") or ""
        text_pages.append(text)
        total_text_len += len(text.strip())

        if use_ocr or use_layout:
            img = render_pdf_page_to_image(page)
            images.append(img)

    is_scanned = total_text_len < 20 and len(text_pages) > 0

    # Extract table of contents
    toc = doc.get_toc(simple=False) if hasattr(doc, "get_toc") else []

    # Extract figures, tables, equations, references
    figures = extract_figures_from_pdf(doc)
    tables = extract_tables_from_pdf(doc)
    equations = extract_equations_from_pdf(doc)
    references = extract_references_from_pdf(doc, text_pages)

    return ParsedDocument(
        source_path=pdf_path,
        is_scanned=is_scanned,
        text_pages=text_pages,
        images=images,
        metadata={
            "pages": len(doc),
            "toc": toc,
            "figures": figures,
            "tables": tables,
            "equations": equations,
            "references": references,
        },
    )


def extract_text_from_docx(docx_path: str) -> ParsedDocument:
    """Extract text from a DOCX document.

    Args:
        docx_path: Path to the DOCX file.

    Returns:
        ParsedDocument with extracted text.

    Raises:
        RuntimeError: If python-docx is not available.
    """
    if docx is None:
        raise RuntimeError("python-docx not available")

    d = docx.Document(docx_path)
    paras = [p.text for p in d.paragraphs if p.text and p.text.strip()]
    text = "\n".join(paras)

    return ParsedDocument(
        source_path=docx_path, is_scanned=False, text_pages=[text], images=[], metadata={}
    )


def extract_text_from_tex(tex_path: str) -> ParsedDocument:
    """Extract text from a LaTeX document.

    Performs lightweight parsing: removes comments, strips LaTeX commands,
    and preserves section headings.

    Args:
        tex_path: Path to the TEX file.

    Returns:
        ParsedDocument with extracted text.
    """
    text = pathlib.Path(tex_path).read_text(encoding="utf-8", errors="ignore")

    # Remove comments
    text = re.sub(r"%.*", "", text)

    # Remove begin/end blocks
    text = re.sub(r"\\begin\{.*?\}|\\end\{.*?\}", " ", text)

    # Preserve section headings
    text = re.sub(r"\\(section|subsection|subsubsection)\*?\{([^}]*)\}", r"\n\n\2\n\n", text)

    # Remove other LaTeX commands
    text = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^}]*\})?", " ", text)

    # Replace equations with placeholder
    text = re.sub(r"\$[^$]*\$", " <EQUATION> ", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return ParsedDocument(
        source_path=tex_path, is_scanned=False, text_pages=[text.strip()], images=[], metadata={}
    )


def extract_text_from_jats(xml_path: str) -> ParsedDocument:
    """Extract text from a JATS XML document.

    Args:
        xml_path: Path to the XML file.

    Returns:
        ParsedDocument with extracted text.

    Raises:
        RuntimeError: If lxml is not available.
    """
    if ET is None:
        raise RuntimeError("lxml not available")

    tree = ET.parse(xml_path)
    root = tree.getroot()
    ns = root.nsmap.get(None) or root.nsmap.get("jats") or ""

    def xp(path):
        return root.xpath(path, namespaces={"j": ns}) if ns else root.xpath(path)

    # Extract title
    title_nodes = xp(".//j:article-title") if ns else root.findall(".//article-title")
    titles = ["".join(t.itertext()).strip() for t in title_nodes]

    # Extract abstract
    abstract_nodes = xp(".//j:abstract") if ns else root.findall(".//abstract")
    abstracts = ["".join(a.itertext()).strip() for a in abstract_nodes]

    # Extract sections
    secs = xp(".//j:sec") if ns else root.findall(".//sec")
    sections: list[str] = []

    for s in secs:
        heading = ""
        if ns:
            title_elem = s.find(".//j:title", namespaces={"j": ns})
            if title_elem is not None:
                heading = "".join(title_elem.itertext())
        else:
            title_elem = s.find(".//title")
            if title_elem is not None:
                heading = "".join(title_elem.itertext())

        body = "".join(s.itertext()).strip()

        if heading:
            sections.append(f"{heading}\n{body}")
        else:
            sections.append(body)

    combined = "\n\n".join(filter(None, titles + abstracts + sections)) or "".join(root.itertext())

    return ParsedDocument(
        source_path=xml_path,
        is_scanned=False,
        text_pages=[combined],
        images=[],
        metadata={"title": titles[0] if titles else ""},
    )


def extract_text_from_txt(txt_path: str) -> ParsedDocument:
    """Extract text from a plain text file.

    Args:
        txt_path: Path to the TXT file.

    Returns:
        ParsedDocument with extracted text.
    """
    text = pathlib.Path(txt_path).read_text(encoding="utf-8", errors="ignore")

    return ParsedDocument(
        source_path=txt_path, is_scanned=False, text_pages=[text], images=[], metadata={}
    )


def ingest(file_path: str, use_ocr: bool = False, use_layout: bool = False) -> ParsedDocument:
    """Ingest a document and extract its text.

    Args:
        file_path: Path to the document.
        use_ocr: Whether OCR might be needed for PDFs.
        use_layout: Whether layout analysis might be needed for PDFs.

    Returns:
        ParsedDocument with extracted text.

    Raises:
        ValueError: If format is not supported.
    """
    fmt = detect_format(file_path)

    if fmt == "pdf":
        return extract_text_from_pdf(file_path, use_ocr, use_layout)
    if fmt == "docx":
        return extract_text_from_docx(file_path)
    if fmt == "tex":
        return extract_text_from_tex(file_path)
    if fmt == "xml":
        return extract_text_from_jats(file_path)
    if fmt == "txt":
        return extract_text_from_txt(file_path)

    raise ValueError(f"Unsupported format: {fmt}")
