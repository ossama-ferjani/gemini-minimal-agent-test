#!/usr/bin/env python3
"""
Register this folder as a pipeline (no Git) and trigger one manual run.

Prerequisites:
  - Kyklos already listening (default http://127.0.0.1:8080)
  - Kyklos server process started with GOOGLE_API_KEY in its environment
    (export GOOGLE_API_KEY=... before `make run` / `go run ./cmd/kyklos`)
  - Step Python has: pip install google-generativeai

Do not put your API key in this file or in git. Use your shell only.

Usage:
  export GOOGLE_API_KEY="your-key"   # before starting Kyklos, same machine
  # terminal 1: (from kyklos repo) KYKLOS_STEPS_DIR=$PWD/steps make run
  # terminal 2:
  python3 trigger-local-run.py

Env:
  BASE_URL  default http://127.0.0.1:8080
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = os.environ.get("BASE_URL", "http://127.0.0.1:8080").rstrip("/")
API = f"{BASE}/api/v1"
ROOT = Path(__file__).resolve().parent


def post_json(path: str, body: dict) -> dict:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"{API}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def wait_health() -> None:
    deadline = time.time() + 30
    while time.time() < deadline:
        try:
            urllib.request.urlopen(urllib.request.Request(f"{BASE}/health", method="GET"), timeout=2)
            return
        except (urllib.error.URLError, TimeoutError):
            time.sleep(0.3)
    print("error: Kyklos not reachable at", BASE, file=sys.stderr)
    sys.exit(1)


def main() -> None:
    wait_health()

    yaml_path = ROOT / "kyklos.yaml"
    if not yaml_path.is_file():
        print("error: kyklos.yaml not next to this script:", yaml_path, file=sys.stderr)
        sys.exit(1)

    # Key is read by Kyklos when expanding env: in YAML — must be set where kyklos runs.
    if not os.environ.get("GOOGLE_API_KEY"):
        print(
            "warning: GOOGLE_API_KEY is not set in *this* shell.\n"
            "  It must be set in the environment of the running Kyklos server.\n"
            "  Restart Kyklos after: export GOOGLE_API_KEY=...\n",
            file=sys.stderr,
        )

    body = {
        "name": "gemini-minimal-local",
        "repo_name": "",
        "yaml_path": "kyklos.yaml",
        "yaml": yaml_path.read_text(encoding="utf-8"),
    }
    created = post_json("/pipelines/", body)
    pid = created.get("id")
    if not pid:
        print("error creating pipeline:", created, file=sys.stderr)
        sys.exit(1)

    ws = str(ROOT)
    trigger = json.dumps({"workspace_path": ws}).encode("utf-8")
    req = urllib.request.Request(
        f"{API}/pipelines/{pid}/runs",
        data=trigger,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60):
        pass

    print("Pipeline id:", pid)
    print("Workspace:", ws)
    print("Open:", f"{BASE}/")
    print("Runs:   ", f"{BASE}/runs")


if __name__ == "__main__":
    main()
