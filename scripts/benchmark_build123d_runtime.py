from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

IMAGE = "ghcr.io/brainboxemb/cad-reference:v0.3.1"\nPYTHON = "/opt/build123d/bin/python"
COUNT = 10
ROUNDS = 3
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)


def run_container(args: list[str]) -> tuple[float, dict]:
    command = [
        "docker", "run", "--rm",
        "-v", f"{ROOT}:/workspace:ro",
        "-w", "/workspace",
        IMAGE,
        PYTHON, "scripts/build123d_worker.py",
        *args,
    ]
    started = time.perf_counter()
    completed = subprocess.run(command, check=True, text=True, capture_output=True)
    elapsed = time.perf_counter() - started
    payload = json.loads(completed.stdout.strip().splitlines()[-1])
    return elapsed, payload


def run_separate() -> dict:
    started = time.perf_counter()
    invocations = []
    for index in range(1, COUNT + 1):
        elapsed, payload = run_container(["--case", str(index)])
        invocations.append({"wall_seconds": elapsed, **payload})
    return {
        "mode": "separate",
        "wall_seconds": time.perf_counter() - started,
        "invocations": invocations,
    }


def run_batch() -> dict:
    started = time.perf_counter()
    elapsed, payload = run_container(["--count", str(COUNT)])
    return {
        "mode": "batch",
        "wall_seconds": time.perf_counter() - started,
        "container_wall_seconds": elapsed,
        "invocation": payload,
    }


def main() -> None:
    subprocess.run(["docker", "pull", IMAGE], check=True)

    rounds = []
    for round_index in range(1, ROUNDS + 1):
        order = ("separate", "batch") if round_index % 2 else ("batch", "separate")
        result = {"round": round_index, "order": list(order)}
        for mode in order:
            result[mode] = run_separate() if mode == "separate" else run_batch()
        rounds.append(result)

    separate = [round_["separate"]["wall_seconds"] for round_ in rounds]
    batch = [round_["batch"]["wall_seconds"] for round_ in rounds]
    avg_separate = sum(separate) / len(separate)
    avg_batch = sum(batch) / len(batch)
    speedup = avg_separate / avg_batch

    data = {
        "image": IMAGE,
        "case_count": COUNT,
        "round_count": ROUNDS,
        "rounds": rounds,
        "average_separate_seconds": avg_separate,
        "average_batch_seconds": avg_batch,
        "speedup": speedup,
        "saved_seconds": avg_separate - avg_batch,
    }
    (OUT / "build123d-runtime.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    summary = f"""# build123d runtime reuse result

Image: `{IMAGE}`

Cases per round: {COUNT}

Rounds: {ROUNDS}

| Mode | Average wall time |
| --- | ---: |
| Separate container + Python/build123d startup per case | {avg_separate:.3f} s |
| One container + one Python/build123d startup for all cases | {avg_batch:.3f} s |

Speedup: **{speedup:.2f}x**

Wall time saved per {COUNT} cases: **{avg_separate - avg_batch:.3f} s**

## Interpretation

Both modes execute the same ten build123d build/export operations. The separate mode pays Docker, Python and build123d/OCCT startup ten times. The batch mode pays those startup costs once while retaining individual per-case timings in the JSON evidence.
"""
    (OUT / "build123d-runtime.md").write_text(summary, encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
