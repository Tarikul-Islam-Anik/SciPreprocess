from __future__ import annotations

from scipreprocess.local_extract import extract_authors_strict


def test_extract_authors_strict_simple_line():
    pages = [
        """
        Awesome Paper Title
        John Doe, Jane Smith and A. B. Clark
        Abstract
        This is the abstract...
        """
    ]
    authors = extract_authors_strict(pages)
    fulls = {a["full"] for a in authors}
    assert any("John" in a and "Doe" in a for a in fulls)
    assert any("Jane" in a and "Smith" in a for a in fulls)


def test_extract_authors_strict_ignores_non_names():
    pages = [
        """
        Proceedings of the 2023 Conference on Something
        pages 495-507
        Abstract
        content
        """
    ]
    authors = extract_authors_strict(pages)
    assert authors == []
