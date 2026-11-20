# CAD runtime performance experiment

Controlled microbenchmarks for CAD runtime startup and reuse.

## Issue #1 — build123d runtime reuse

The first experiment compares the current reference-style execution boundary with a batched build123d runtime using the exact released reference image:

`ghcr.io/brainboxemb/cad-reference:v0.3.1`

Each round executes the same ten small build/export operations.

- **separate**: ten fresh Docker containers; each starts Python and imports build123d/OCCT.
- **batch**: one Docker container and one Python process; build123d/OCCT is imported once, then all ten cases run.

The workflow runs three rounds and alternates execution order to reduce simple warm-order bias. Raw timings are stored in `results/build123d-runtime.json`; the concise conclusion is stored in `results/build123d-runtime.md`.

This repository contains experimental evidence only. Production CAD-CI changes belong in their owning repositories after the result is known.
