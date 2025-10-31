use std::collections::HashSet;

use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::{PyAny, PyDict, PyList};
use regex::Regex;

fn extract_figures(py: Python<'_>, text_pages: &[String]) -> PyResult<Vec<PyObject>> {
    let figure_pattern = Regex::new(r"(?i)(Figure|Fig\.?)(?-i)\s+(\d+)")
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
    let mut figures: Vec<PyObject> = Vec::new();

    for (page_idx, text) in text_pages.iter().enumerate() {
        for caps in figure_pattern.captures_iter(text) {
            let start = caps.get(0).map(|m| m.start()).unwrap_or(0);
            let end = std::cmp::min(start + 300, text.len());
            let mut caption = &text[start..end];
            if let Some(pos) = caption.find("\n\n") {
                caption = &caption[..pos];
            }

            let entry = PyDict::new(py);
            entry.set_item("type", "figure")?;
            entry.set_item("number", caps.get(2).map(|m| m.as_str()).unwrap_or(""))?;
            entry.set_item("caption", caption.trim())?;
            entry.set_item("page", page_idx + 1)?;
            figures.push(entry.into());
        }
    }

    Ok(figures)
}

fn extract_tables(py: Python<'_>, text_pages: &[String]) -> PyResult<Vec<PyObject>> {
    let table_pattern = Regex::new(r"(?i)Table\s+(\d+)")
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
    let mut tables: Vec<PyObject> = Vec::new();

    for (page_idx, text) in text_pages.iter().enumerate() {
        for caps in table_pattern.captures_iter(text) {
            let start = caps.get(0).map(|m| m.start()).unwrap_or(0);
            let end = std::cmp::min(start + 300, text.len());
            let mut caption = &text[start..end];
            if let Some(pos) = caption.find("\n\n") {
                caption = &caption[..pos];
            }

            let entry = PyDict::new(py);
            entry.set_item("type", "table")?;
            entry.set_item("number", caps.get(1).map(|m| m.as_str()).unwrap_or(""))?;
            entry.set_item("caption", caption.trim())?;
            entry.set_item("page", page_idx + 1)?;
            tables.push(entry.into());
        }
    }

    Ok(tables)
}

fn extract_equations(py: Python<'_>, text_pages: &[String]) -> PyResult<Vec<PyObject>> {
    let eq_pattern = Regex::new(r"(?i)(Equation|Eq\.?)\s*[\(\[]?(\d+)[\)\]]?")
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
    let numbered_pattern = Regex::new(r"(?m)\((\d+)\)\s*$")
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
    let mut equations: Vec<PyObject> = Vec::new();

    for (page_idx, text) in text_pages.iter().enumerate() {
        let mut seen: HashSet<String> = HashSet::new();

        for caps in eq_pattern.captures_iter(text) {
            if let Some(num) = caps.get(2) {
                let number = num.as_str().to_string();
                if seen.insert(number.clone()) {
                    let entry = PyDict::new(py);
                    entry.set_item("type", "equation")?;
                    entry.set_item("number", number)?;
                    entry.set_item("page", page_idx + 1)?;
                    equations.push(entry.into());
                }
            }
        }

        for caps in numbered_pattern.captures_iter(text) {
            if let Some(num) = caps.get(1) {
                let number = num.as_str().to_string();
                if seen.insert(number.clone()) {
                    let entry = PyDict::new(py);
                    entry.set_item("type", "equation")?;
                    entry.set_item("number", number)?;
                    entry.set_item("page", page_idx + 1)?;
                    equations.push(entry.into());
                }
            }
        }
    }

    Ok(equations)
}

fn extract_references(py: Python<'_>, text_pages: &[String]) -> PyResult<Vec<PyObject>> {
    let join_text = text_pages.join("\n");
    let ref_pattern = Regex::new(r"\n\s*(References|REFERENCES|Bibliography|BIBLIOGRAPHY)\s*\n")
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;

    let Some(ref_match) = ref_pattern.find(&join_text) else {
        return Ok(Vec::new());
    };

    let mut remainder = &join_text[ref_match.end()..];
    let end_patterns = [
        Regex::new(r"\n\s*(Appendix|APPENDIX|Acknowledgments|ACKNOWLEDGMENTS)\s*\n")
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))?,
    ];

    for pat in &end_patterns {
        if let Some(m) = pat.find(remainder) {
            remainder = &remainder[..m.start()];
            break;
        }
    }

    let number_pattern = Regex::new(r"\n\s*(?:\[(\d+)\]|(\d+)\.)\s+")
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;

    let mut refs: Vec<(String, String)> = Vec::new();
    let mut last_index = 0usize;
    let mut current_number: Option<String> = None;

    for caps in number_pattern.captures_iter(remainder) {
        if let Some(m) = caps.get(0) {
            let segment = &remainder[last_index..m.start()];
            if let Some(number) = current_number.take() {
                let text = segment.trim();
                if !text.is_empty() {
                    refs.push((number, text.to_string()));
                }
            }

            if let Some(n) = caps.get(1).or_else(|| caps.get(2)) {
                current_number = Some(n.as_str().to_string());
            }
            last_index = m.end();
        }
    }

    let tail = remainder[last_index..].trim();
    if let Some(number) = current_number {
        if !tail.is_empty() {
            refs.push((number, tail.to_string()));
        }
    }

    if refs.is_empty() {
        for (idx, line) in remainder.lines().enumerate() {
            let trimmed = line.trim();
            if trimmed.len() > 20 {
                refs.push(((idx + 1).to_string(), trimmed.to_string()));
            }
        }
    }

    let mut out: Vec<PyObject> = Vec::with_capacity(refs.len());
    for (number, text) in refs {
        let entry = PyDict::new(py);
        entry.set_item("number", number)?;
        entry.set_item("text", text)?;
        out.push(entry.into());
    }

    Ok(out)
}

#[pyfunction]
fn extract_text_from_pdf(
    py: Python<'_>,
    pdf_path: &str,
    use_ocr: bool,
    use_layout: bool,
) -> PyResult<PyObject> {
    let fitz = py.import("fitz").map_err(|_| PyRuntimeError::new_err("PyMuPDF not available"))?;
    let doc = fitz.call_method1("open", (pdf_path,))?;
    let page_count: usize = doc.call_method0("__len__")?.extract()?;

    let mut text_pages: Vec<String> = Vec::with_capacity(page_count);
    let mut total_len = 0usize;
    let mut images: Vec<PyObject> = Vec::new();

    let render_helper: Option<Py<PyAny>> = if use_ocr || use_layout {
        let module = py.import("scipreprocess.parsers")?;
        Some(module.getattr("render_pdf_page_to_image")?.into())
    } else {
        None
    };

    for idx in 0..page_count {
        let page_any = doc.call_method1("__getitem__", (idx,))?;
        let page_obj: Py<PyAny> = page_any.into_py(py);
        let text: String = page_obj
            .call_method1(py, "get_text", ("text",))?
            .extract(py)?;
        total_len += text.trim().len();
        if let Some(helper) = &render_helper {
            let img = helper
                .as_ref(py)
                .call1((page_obj.as_ref(py),))?
                .into_py(py);
            images.push(img);
        }
        text_pages.push(text);
    }

    let is_scanned = page_count > 0 && total_len < 20;

    let toc_obj = match doc.getattr("get_toc") {
        Ok(method) => {
            let kwargs = PyDict::new(py);
            kwargs.set_item("simple", false)?;
            method.call((), Some(kwargs))?.into_py(py)
        }
        Err(_) => py.None().into_py(py),
    };

    let figures = extract_figures(py, &text_pages)?;
    let tables = extract_tables(py, &text_pages)?;
    let equations = extract_equations(py, &text_pages)?;
    let references = extract_references(py, &text_pages)?;

    let metadata = PyDict::new(py);
    metadata.set_item("pages", page_count)?;
    metadata.set_item("toc", toc_obj)?;
    metadata.set_item("figures", PyList::new(py, &figures))?;
    metadata.set_item("tables", PyList::new(py, &tables))?;
    metadata.set_item("equations", PyList::new(py, &equations))?;
    metadata.set_item("references", PyList::new(py, &references))?;

    let result = PyDict::new(py);
    result.set_item("pages", PyList::new(py, &text_pages))?;
    result.set_item("images", PyList::new(py, &images))?;
    result.set_item("metadata", metadata)?;
    result.set_item("is_scanned", is_scanned)?;

    Ok(result.into())
}

#[pymodule]
fn pdf_ingest_rs(py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(extract_text_from_pdf, m)?)?;
    m.add("__all__", PyList::new(py, &["extract_text_from_pdf"]))?;
    Ok(())
}
