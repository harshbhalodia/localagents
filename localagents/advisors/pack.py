"""The advisor-pack format and its validator.

The fields mirror what Loonie reads (see its `services/marketplace_catalog.py`), so a pack that
validates here loads there. Errors block publishing; warnings are advice to make the pack better.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

KINDS = ("stress_test", "decision", "analysis", "plan")

# The user data categories Loonie can hand an advisor. Anything else is ignored by Loonie.
LOONIE_SCOPES = (
    "net_worth",
    "liquidity",
    "cashflow",
    "diversification",
    "income_forecast",
    "goal_feasibility",
)


@dataclass
class PackReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


@dataclass
class AdvisorPack:
    id: str
    name: str
    publisher: str
    version: str
    kind: str
    summary: str
    triggers: list[str]
    examples: list[str]
    inputs: list[str]
    scenarios: list[dict[str, str]]
    raw: dict[str, Any]


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _string_list(value: Any) -> list[str]:
    return [str(v).strip() for v in value if str(v).strip()] if isinstance(value, list) else []


def validate_pack(raw: Any) -> PackReport:
    report = PackReport()
    if not isinstance(raw, dict):
        report.errors.append("The file must be a YAML mapping (key: value pairs).")
        return report

    for key in ("id", "name", "publisher"):
        if not _text(raw.get(key)):
            report.errors.append(f"Missing '{key}'.")

    kind = _text(raw.get("kind")) or "stress_test"
    if kind not in KINDS:
        report.errors.append(f"'kind' must be one of: {', '.join(KINDS)} (got '{kind}').")

    scenarios = raw.get("scenarios")
    valid_scenarios = [
        s for s in (scenarios if isinstance(scenarios, list) else []) if isinstance(s, dict) and _text(s.get("id")) and _text(s.get("description"))
    ]
    if not valid_scenarios:
        report.errors.append("Add at least one scenario, each with an 'id' and a 'description'.")
    elif len({_text(s["id"]) for s in valid_scenarios}) != len(valid_scenarios):
        report.errors.append("Scenario ids must be unique.")

    inputs = _string_list(raw.get("inputs"))
    unknown = [i for i in inputs if i not in LOONIE_SCOPES]
    if unknown:
        report.warnings.append(f"Loonie ignores unknown inputs: {', '.join(unknown)}. Known: {', '.join(LOONIE_SCOPES)}.")
    if not inputs:
        report.warnings.append("No 'inputs': the advisor would see none of the user's numbers, so it can only give generic advice.")
    if not _string_list(raw.get("triggers")):
        report.warnings.append("No 'triggers': Loonie can only start this advisor by its name. Add phrases like 'job loss'.")
    if not _string_list(raw.get("examples")):
        report.warnings.append("No 'examples': users get no suggested questions for it.")
    if len(_text(raw.get("summary"))) < 20:
        report.warnings.append("Write a one-sentence 'summary' (users see it).")
    if not _text(raw.get("disclaimer")):
        report.warnings.append("No 'disclaimer': Loonie will append its generic one.")
    return report


def load_pack(path: str | Path) -> AdvisorPack:
    """Reads and validates a pack file. Raises ValueError listing every error."""
    file = Path(path)
    try:
        raw = yaml.safe_load(file.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"Could not read {file}: {exc}") from exc

    report = validate_pack(raw)
    if not report.ok:
        raise ValueError("; ".join(report.errors))

    scenarios = [{"id": _text(s["id"]), "description": _text(s["description"])} for s in raw["scenarios"] if isinstance(s, dict)]
    return AdvisorPack(
        id=_text(raw["id"]),
        name=_text(raw["name"]),
        publisher=_text(raw["publisher"]),
        version=_text(raw.get("version")) or "0.1.0",
        kind=_text(raw.get("kind")) or "stress_test",
        summary=_text(raw.get("summary")),
        triggers=_string_list(raw.get("triggers")),
        examples=_string_list(raw.get("examples")),
        inputs=_string_list(raw.get("inputs")),
        scenarios=scenarios,
        raw=raw,
    )


_TEMPLATE = """\
# An advisor pack: plain data that Loonie loads. No code, nothing to install.
id: {id}
name: {name}
publisher: {publisher}
version: "0.1.0"
kind: {kind}            # stress_test | decision | analysis | plan

# One plain sentence. Users see this.
summary: {summary}

# Phrases that make Loonie pick this advisor when someone says them.
triggers:
  - job loss
  - lose my job

# Ready-made questions shown as suggestions.
examples:
  - What if I lose my job for 3 months?

# The user's numbers this advisor may read. Loonie asks the user before sharing any.
# Options: {scopes}
inputs:
  - net_worth
  - liquidity
  - cashflow

# Each scenario is analysed on its own, then combined into one advisory.
scenarios:
  - id: job_loss_3mo
    description: Primary income drops to zero for 3 months, then fully recovers.
  - id: rate_shock_2pt
    description: Variable interest rates rise by 2 percentage points for a year.

# Optional: your own wording. Leave out to use Loonie's defaults.
# specialist_system_prompt: ...
# lead_system_prompt: ... (end with {{disclaimer}})
disclaimer: >
  Automated, informational analysis from your own figures. Not personal financial advice.
"""


def render_template(*, id: str, name: str, publisher: str, kind: str = "stress_test", summary: str = "") -> str:
    return _TEMPLATE.format(
        id=id,
        name=name,
        publisher=publisher,
        kind=kind,
        summary=summary or "Explain in one sentence what this advisor checks and for whom.",
        scopes=", ".join(LOONIE_SCOPES),
    )
