#!/usr/bin/env python3
"""Measure full versus headless CadQuery Docker images."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess


IMAGES = {
    "full": "cadquery-full:experiment",
    "headless": "cadquery-headless:experiment",
}
OUT = Path("results")
OUT.mkdir(exist_ok=True)


def output(*args: str) -> str:
    return subprocess.check_output(args, text=True).strip()


def compressed_size(image: str) -> int:
    command = f"docker save {image} | gzip -1 | wc -c"
    return int(subprocess.check_output(command, shell=True, text=True).strip())


def packages(image: str) -> list[str]:
    text = output(
        "docker",
        "run",
        "--rm",
        image,
        "python",
        "-m",
        "pip",
        "freeze",
    )
    keys = ("cadquery", "ocp", "vtk", "trame", "casadi", "numba", "scipy")
    return [
        line
        for line in text.splitlines()
        if any(key in line.lower() for key in keys)
    ]


def main() -> None:
    rows = {}
    for mode, image in IMAGES.items():
        rows[mode] = {
            "image": image,
            "docker_size_bytes": int(
                output("docker", "image", "inspect", image, "--format", "{{.Size}}")
            ),
            "gzip_save_bytes": compressed_size(image),
            "packages": packages(image),
        }

    full = rows["full"]
    headless = rows["headless"]
    result = {
        "images": rows,
        "docker_size_saved_bytes": (
            full["docker_size_bytes"] - headless["docker_size_bytes"]
        ),
        "gzip_save_saved_bytes": (
            full["gzip_save_bytes"] - headless["gzip_save_bytes"]
        ),
        "docker_size_ratio": (
            headless["docker_size_bytes"] / full["docker_size_bytes"]
        ),
        "gzip_save_ratio": (
            headless["gzip_save_bytes"] / full["gzip_save_bytes"]
        ),
    }
    (OUT / "cadquery-headless.json").write_text(
        json.dumps(result, indent=2) + "\n",
        encoding="utf-8",
    )

    mib = 1024 * 1024
    markdown = f"""# CadQuery headless runtime footprint

Both images use the same pinned Python 3.12 slim base and system libraries.
Both build a box with a hole and export a non-empty STL during image build.

| Mode | Docker size | gzip docker-save |
| --- | ---: | ---: |
| Normal CadQuery 2.8.0 | {full['docker_size_bytes']/mib:.1f} MiB | {full['gzip_save_bytes']/mib:.1f} MiB |
| Headless CadQuery 2.8.0 + OCP-no-VTK | {headless['docker_size_bytes']/mib:.1f} MiB | {headless['gzip_save_bytes']/mib:.1f} MiB |

Docker size saved: **{result['docker_size_saved_bytes']/mib:.1f} MiB**
({(1-result['docker_size_ratio'])*100:.1f}%).

Compressed save size saved: **{result['gzip_save_saved_bytes']/mib:.1f} MiB**
({(1-result['gzip_save_ratio'])*100:.1f}%).

## Relevant packages

### Full

```
{chr(10).join(full['packages'])}
```

### Headless

```
{chr(10).join(headless['packages'])}
```
"""
    (OUT / "cadquery-headless.md").write_text(markdown, encoding="utf-8")
    print(markdown)


if __name__ == "__main__":
    main()
