"""Real-world LocalAgents example: an orchestrated wealth-advisory review over a live Loonie
(lifeos) account's actual financial data, using a local LM Studio model for inference.

Setup:
    1. Have Loonie's backend running (default http://127.0.0.1:8000) with some wealth data
       entered.
    2. Have LM Studio serving a model at the "simple" endpoint configured in config.yaml
       (POST {model, system_prompt, input} -> text), e.g. http://localhost:1234/api/v1/chat.
       Copy config.example.yaml to config.yaml first if you haven't already.
    3. Set credentials via environment variables (never hardcode credentials in source):
         $env:LIFEOS_EMAIL = "you@example.com"     # PowerShell; `export` on macOS/Linux
         $env:LIFEOS_PASSWORD = "..."

Run:
    python examples/wealth_advisor_review.py
"""
from __future__ import annotations

import os
from pathlib import Path

from localagents import Harness
from localagents.agents.wealth_advisor import LifeosClient, run_wealth_advisor_review

LIFEOS_BASE_URL = os.environ.get("LIFEOS_BASE_URL", "http://127.0.0.1:8000")
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"


def main() -> None:
    email = os.environ.get("LIFEOS_EMAIL")
    password = os.environ.get("LIFEOS_PASSWORD")
    if not email or not password:
        raise SystemExit(
            "Set LIFEOS_EMAIL and LIFEOS_PASSWORD environment variables first "
            "(never hardcode credentials in source)."
        )

    client = LifeosClient.login(LIFEOS_BASE_URL, email, password)
    snapshot = client.fetch_wealth_snapshot()

    harness = Harness.from_file(CONFIG_PATH)
    review = run_wealth_advisor_review(harness, snapshot)
    print(review)


if __name__ == "__main__":
    main()
