"""Runs the free "Loonie Core Stress Test" example blueprint against a real Loonie backend
snapshot, using the same env-var-based login pattern as `wealth_advisor_review.py`.

    LIFEOS_EMAIL=you@example.com LIFEOS_PASSWORD=... python examples/stress_test_blueprint.py
"""
from __future__ import annotations

import os

from localagents.agents.wealth_advisor import LifeosClient
from localagents.blueprints import load_blueprint
from localagents.harness import Harness

BLUEPRINT_DIR = "examples/blueprints/loonie_core_stress_test"


def main() -> None:
    email = os.environ["LIFEOS_EMAIL"]
    password = os.environ["LIFEOS_PASSWORD"]
    base_url = os.environ.get("LIFEOS_BASE_URL", "http://localhost:8000")

    client = LifeosClient.login(base_url, email, password)
    snapshot = client.fetch_wealth_snapshot()

    blueprint = load_blueprint(BLUEPRINT_DIR)
    harness = Harness.from_file(os.environ.get("LOCALAGENTS_CONFIG", "config.yaml"))
    print(blueprint.run(harness, snapshot=snapshot))


if __name__ == "__main__":
    main()
