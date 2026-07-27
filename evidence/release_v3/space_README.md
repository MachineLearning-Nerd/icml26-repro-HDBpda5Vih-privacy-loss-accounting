---
title: "Reproduction Efficient Privacy Loss Accounting"
emoji: 🎯
colorFrom: blue
colorTo: green
sdk: static
pinned: false
tags:
 - icml2026-repro
 - paper-HDBpda5Vih
---

# Exact registered-claim reproduction

This additive release preserves the prior judged logbook and exposes the actual
CPU verifier used for all six registered claims.

```bash
uv sync --frozen
uv run --frozen python repro/src/verify_pld.py
```

Claims 1–4 are verified. Claims 5–6 are literally falsified because the
registered figure locators are wrong, while their substantive Bernoulli and
PREAMBLE results are independently verified. See the top-level exact claim
pages for source, code, raw data, independent checkers, and negative controls.
