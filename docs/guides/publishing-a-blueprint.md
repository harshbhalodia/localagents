# Guide: publishing a blueprint (creators, advisors, banks)

This guide walks through authoring a new blueprint end to end, from scaffold to a
marketplace-ready package. It applies equally to an independent community creator and to a
bank's advisory content team — there is no separate tooling for "official" publishers today
(see the architecture doc's trust-model roadmap for the certification step that's coming).

## 1. Scaffold

```bash
pip install localagents
localagents blueprint init my_bank_stress_test --id my_bank.stress_test --publisher "My Bank"
```

This creates:

```
my_bank_stress_test/
├── blueprint.yaml   # manifest — edit this
└── agent.py         # entry point — edit this
```

## 2. Edit the manifest (`blueprint.yaml`)

```yaml
id: my_bank.stress_test          # globally unique — "publisher_slug.blueprint_slug" convention
name: My Bank Stress Test
version: 0.1.0                   # bump on every change you publish
publisher: My Bank
tier: free                       # or "paid"
price_usd: null                  # required if tier is "paid" (must be > 0)
category: stress_test
summary: >
  One or two sentences describing what this blueprint does and who it's for — shown in the
  marketplace catalog.
entry: agent:run                 # module:function — the callable the loader invokes
inputs:                          # which computed-snapshot fields you read (documentation +
  - net_worth                    # future enforcement point, see architecture doc section 4)
  - liquidity
tags:
  - stress-test
```

Validate it any time with `localagents blueprint validate my_bank_stress_test`.

## 3. Write the agent logic (`agent.py`)

Follow the grounded-facts pattern used by every blueprint in this repo (see
`examples/blueprints/loonie_core_stress_test/agent.py` and
`examples/blueprints/maple_trust_advisory_stress_test/agent.py` for full examples):

- **Never let the model invent numbers.** Only pass it pre-computed figures from the `snapshot`
  dict your entry point receives — never raw records, never numbers the model estimates itself.
- **One specialist per scenario/shock**, each with a narrow system prompt and only the facts
  relevant to that scenario.
- **One lead/synthesis call** at the end that combines the specialist notes into a single
  client-facing narrative with a fixed structure.
- **Always end with a disclaimer line** stating this is an automated, informational summary,
  not licensed financial advice.

Minimal shape:

```python
from localagents.agents import register

@register("my_bank.stress_test")
def run(harness, snapshot=None, **kwargs):
    snapshot = snapshot or {}
    agent = harness.build_agent(system_prompt="...")
    return str(agent(f"...{snapshot}..."))
```

## 4. Test it locally against your own data

Never test against a real customer's data you don't have explicit rights to use. Test either
with synthetic data or your own account:

```python
from localagents.blueprints import load_blueprint
from localagents.harness import Harness

blueprint = load_blueprint("my_bank_stress_test")
harness = Harness.from_file("config.yaml")
print(blueprint.run(harness, snapshot={"net_worth": {...}, "liquidity": {...}}))
```

## 5. Package and submit

Until the hosted marketplace exists, "packaging" is simply zipping the package directory
(`blueprint.yaml` + your entry module) and sending it to the platform for listing. Once the
hosted service ships (architecture doc, section 5), this becomes:

```bash
localagents blueprint pack my_bank_stress_test        # produces my_bank_stress_test.zip
localagents blueprint publish my_bank_stress_test.zip --api-key <your-publisher-key>
```

(`pack`/`publish` are not implemented yet in v0.1 — track this guide's revision history or the
`localagents` `CHANGELOG.md` for when they land.)

## 6. Pricing guidance for paid blueprints

- Price in whole-dollar-or-cents USD (`price_usd` in the manifest); the marketplace handles
  currency conversion/display at listing time.
- A paid blueprint should offer something a free one genuinely can't: more scenarios, sharper
  bank-specific assumptions, a distinctive advisory voice/brand — not just "the same content,
  paywalled." Users can always see a blueprint's declared `inputs`/`category`/`summary` before
  buying, so undifferentiated paid content will be visibly weaker in the catalog next to strong
  free alternatives.

## 7. Certification (roadmap)

Publisher signing and a lightweight content review are planned (architecture doc, section 4)
before third-party submissions open broadly. A "Verified Publisher" badge will be a real
cryptographic + review claim, not just a marketplace label — banks and licensed advisors should
expect to go through this step before publishing at scale.
