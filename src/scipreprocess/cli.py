from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .pipeline import PreprocessingPipeline
from .config import PipelineConfig


def main() -> int:
    p = argparse.ArgumentParser(prog="scipreprocess", description="Preprocess documents with optional Docling backend")
    p.add_argument("inputs", nargs="+", help="Paths to documents")
    p.add_argument("--backend", choices=["auto", "docling", "local"], default="auto")
    p.add_argument("--ocr", action="store_true")
    p.add_argument("--layout", action="store_true")
    p.add_argument("--lower", action="store_true")
    p.add_argument("--out", type=str, default="-")
    args = p.parse_args()

    cfg = PipelineConfig(
        use_ocr=args.ocr,
        use_layout=args.layout,
        parser_backend=args.backend,  # type: ignore[arg-type]
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

    output = json.dumps(result, ensure_ascii=False)
    if args.out == "-":
        print(output)
    else:
        Path(args.out).write_text(output, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())


