from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import PipelineConfig
from .pipeline import PreprocessingPipeline
from .utils import serialize_output


def main() -> int:
    p = argparse.ArgumentParser(
        prog="scipreprocess", description="Preprocess documents with optional Docling backend"
    )
    p.add_argument("inputs", nargs="+", help="Paths to documents")
    p.add_argument("--backend", choices=["auto", "docling", "local"], default="auto")
    p.add_argument("--ocr", action="store_true")
    p.add_argument("--layout", action="store_true")
    p.add_argument("--lower", action="store_true")
    p.add_argument("--out", type=str, default="-")
    p.add_argument(
        "--format", choices=["json", "csv"], default="json", help="Output format (default: json)"
    )
    args = p.parse_args()

    cfg = PipelineConfig(
        use_ocr=args.ocr,
        use_layout=args.layout,
    )
    pipe = PreprocessingPipeline(cfg)
    inputs = []
    for x in args.inputs:
        px = Path(x)
        if not px.exists():
            print(f"warning: path not found, skipping: {x}", file=sys.stderr)
            continue
        inputs.append(str(px))
    if not inputs:
        print("error: no valid inputs", file=sys.stderr)
        return 2

    result = pipe.preprocess_documents(inputs, lower=args.lower)

    output = serialize_output(result, format=args.format)
    if args.out == "-":
        print(output)
    else:
        Path(args.out).write_text(output, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
