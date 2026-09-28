# Onboarding: running a stress-test blueprint against your own profile

This guide is for end users of a LocalAgents-powered app (e.g. Loonie) who want to run a
blueprint — free or paid, in-house or from a third-party publisher like a bank — against their
own financial profile. Everything below runs on your own machine; nothing you run here uploads
your data anywhere.

## 1. What a blueprint actually does

A blueprint is a small package of advisory logic (a set of scenarios/prompts) plus a manifest
describing who published it and whether it's free or paid. When you "run" a blueprint, the app:

1. Computes your current analytics locally (net worth, liquidity, cashflow, etc. — the same
   numbers you already see on your dashboard).
2. Hands only those already-computed numbers (never raw transactions) to your local AI model.
3. Shows you the model's narrative summary.

The publisher (e.g. a bank) never sees your data — they only ever ship the *logic*, which runs
entirely on your device.

## 2. Prerequisites

- A LocalAgents-powered app installed and connected to a local model (Ollama, LM Studio, or
  similar — see the app's own setup guide for this step).
- At least one blueprint installed (see below).

## 3. Trying it from the command line (developers / early adopters)

```bash
pip install localagents
localagents blueprint list --dir examples/blueprints        # see what's available
localagents blueprint validate examples/blueprints/loonie_core_stress_test
localagents blueprint run examples/blueprints/loonie_core_stress_test --config config.yaml
```

This runs the free, in-house stress test with an empty snapshot (`snapshot=None`). To run it
against real data, see `examples/stress_test_blueprint.py` in the `localagents` repo, which
fetches a real snapshot from a running Loonie backend first.

## 4. Free vs. paid blueprints

- **Free** blueprints (in-house or third-party) always run — no purchase step.
- **Paid** blueprints require a license token, issued by the marketplace at purchase time.
  Until the hosted marketplace exists, this token is provided directly by the publisher; pass it
  with `--license TOKEN --license-secret SECRET` on the CLI, or through the app's own "Enter
  license" flow once that UI ships.

## 5. Choosing a blueprint

Every blueprint's manifest tells you, before you run it:

- **Publisher** — who wrote the logic (e.g. "Loonie (in-house)" vs. a named bank/advisor).
- **Tier and price** — free or paid, and how much.
- **Inputs** — which of your computed figures it reads (e.g. `net_worth`, `liquidity`,
  `goal_feasibility`) — nothing beyond what's listed is ever touched.
- **Category** — e.g. `stress_test` for scenario-based resilience reviews.

Run `localagents blueprint list --dir <installed-blueprints-dir>` to see all of this for every
blueprint you have installed, or check the marketplace catalog once the in-app browsing UI
ships (see the architecture doc's Loonie integration plan).

## 6. Understanding your results

Every blueprint's output ends with a fixed disclaimer line: this is an automated, local-LLM
generated summary of your own numbers — not personalized advice from a licensed advisor, and
not a substitute for talking to one. Use it as a starting point for questions to ask, not as a
final decision.
