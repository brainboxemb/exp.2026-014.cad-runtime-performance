#!/usr/bin/env python3
"""Minimal CadQuery reference-runtime smoke test."""

from pathlib import Path
import sys

import cadquery as cq


target = Path(sys.argv[1])
model = (
    cq.Workplane("XY")
    .box(20, 12, 6)
    .faces(">Z")
    .workplane()
    .hole(3)
)
cq.exporters.export(model, str(target))
if not target.is_file() or target.stat().st_size == 0:
    raise RuntimeError(f"CadQuery did not export a non-empty STL: {target}")
print(f"cadquery smoke: PASS ({target.stat().st_size} bytes)")
