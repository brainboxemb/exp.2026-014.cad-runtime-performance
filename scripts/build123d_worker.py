from __future__ import annotations

import argparse
import importlib.metadata
import json
import tempfile
import time
from pathlib import Path


def build_case(index: int, output_dir: Path) -> dict[str, float | int]:
    from build123d import Box, Cylinder, export_stl

    started = time.perf_counter()
    width = 20 + index
    depth = 12 + (index % 3)
    height = 6 + (index % 2)
    part = Box(width, depth, height) - Cylinder(2 + (index % 2) * 0.25, height)
    build_seconds = time.perf_counter() - started

    export_started = time.perf_counter()
    export_stl(part, output_dir / f"case-{index:02d}.stl")
    export_seconds = time.perf_counter() - export_started

    return {
        "case": index,
        "build_seconds": build_seconds,
        "export_seconds": export_seconds,
        "case_seconds": build_seconds + export_seconds,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", type=int)
    parser.add_argument("--count", type=int)
    args = parser.parse_args()

    import_started = time.perf_counter()
    import build123d  # noqa: F401
    import_seconds = time.perf_counter() - import_started

    with tempfile.TemporaryDirectory() as tmp:
        output_dir = Path(tmp)
        if args.case is not None:
            cases = [build_case(args.case, output_dir)]
        else:
            count = args.count or 10
            cases = [build_case(index, output_dir) for index in range(1, count + 1)]

    print(json.dumps({
        "build123d_version": importlib.metadata.version("build123d"),
        "import_seconds": import_seconds,
        "cases": cases,
    }))


if __name__ == "__main__":
    main()
