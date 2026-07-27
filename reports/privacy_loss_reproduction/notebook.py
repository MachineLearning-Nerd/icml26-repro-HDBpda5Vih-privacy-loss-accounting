import marimo

__generated_with = "0.23.15"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np

    return mo, np, plt


@app.cell
def _(mo, np, plt):
    _matrix = np.ones((6, 3))
    _fig, _ax = plt.subplots(figsize=(8.8, 4.0))
    _ax.imshow(_matrix, cmap="Greens", vmin=0, vmax=1.3, aspect="auto")
    for _row in range(6):
        for _col in range(3):
            _ax.text(
                _col,
                _row,
                "✓",
                ha="center",
                va="center",
                color="white",
                fontsize=17,
                fontweight="bold",
            )
    _ax.set_xticks(
        range(3),
        ["Direct claim\ncontract", "Independent\nchecker", "Negative\ncontrol"],
    )
    _ax.set_yticks(range(6), [f"Claim {_index}" for _index in range(1, 7)])
    _ax.tick_params(length=0)
    for _spine in _ax.spines.values():
        _spine.set_visible(False)
    _fig.tight_layout()
    mo.vstack(
        [
            mo.md(
                """
                # Efficient privacy loss accounting: an executable reproduction

                **Headline evidence:** every claim has a direct, failure-sensitive
                contract, an independent check, and a negative control. These are
                local verdicts; the public judge has not evaluated revision
                `bd20a58` yet.
                """
            ),
            _fig,
        ]
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## The question

    Subsampling and random allocation can reduce privacy loss, but generic amplification is not enough to validate the paper. The reproduction asks six narrower questions: do the exact PLD identities hold, does the released geometric algorithm satisfy its accuracy contract, and do the published numerical comparisons survive at their stated scale?

    The formal command is fixed across every experiment:

    ```bash
    uv run --frozen python repro/src/verify_pld.py
    ```
    """)
    return


@app.cell
def _():
    claim_details = {
        "Claim 1 — exact PLD reduction": (
            "VERIFIED",
            "30 exact add/remove identities, 6 k=2 scope checks, "
            "30/30 mutations rejected.",
        ),
        "Claim 2 — geometric algorithm": (
            "VERIFIED",
            "17 fast-versus-exact and 6 released Gaussian cases; "
            "work exponents 2.487 in log(t) and 1.984 in 1/α.",
        ),
        "Claim 3 — Poisson transformations": (
            "VERIFIED",
            "24 exact φλ transformations and 4 unified composition checks; "
            "24/24 mutations rejected.",
        ),
        "Claim 4 — lower and RDP bounds": (
            "VERIFIED",
            "100 numerical points; median RDP improvement 83.03%; "
            "44 statistically resolved Monte Carlo points.",
        ),
        "Claim 5 — Bernoulli utility": (
            "FALSIFIED as registered; substantive result VERIFIED",
            "n=1,000 and δ=10⁻¹⁰; allocation used 0.21–3.77% less noise "
            "across all three privacy panels. The registered Figure 4 locator "
            "is false; the experiment is Figure 5.",
        ),
        "Claim 6 — PREAMBLE/DP-SGD": (
            "FALSIFIED as registered; substantive result VERIFIED",
            "40/40 full-scale points favored PLD; minimum/median epsilon "
            "improvement 5.99%/26.55%; matched-privacy anchor passed. The "
            "registered Figure 5 locator is false; PREAMBLE is Figure 3.",
        ),
    }
    return (claim_details,)


@app.cell
def _(claim_details, mo):
    claim = mo.ui.dropdown(
        options=list(claim_details),
        value="Claim 6 — PREAMBLE/DP-SGD",
        label="Inspect a claim",
    )
    claim
    return (claim,)


@app.cell
def _(claim, claim_details, mo):
    _verdict, _detail = claim_details[claim.value]
    mo.callout(
        mo.md(f"**{_verdict}** — {_detail}"),
        kind="success",
    )
    return


@app.cell
def _():
    claim6_grid = {
        512: {
            4: (0.799236, 1.04692),
            8: (0.679053, 1.04734),
            16: (0.603623, 1.04823),
            32: (0.572023, 1.05018),
            64: (0.553294, 1.0555),
            128: (0.56441, 1.09446),
            256: (0.603402, 1.18609),
            512: (0.706706, 1.46981),
            1024: (1.28122, 2.95114),
            2048: (5.40296, 8.32301),
        },
        1028: {
            4: (1.07476, 1.25883),
            8: (0.935587, 1.26036),
            16: (0.807649, 1.26373),
            32: (0.80209, 1.27203),
            64: (0.813558, 1.29984),
            128: (0.840143, 1.38381),
            256: (0.902001, 1.50635),
            512: (1.0716, 1.80758),
            1024: (1.90205, 3.14915),
            2048: (6.46249, 12.8201),
        },
        4096: {
            4: (1.82399, 2.36999),
            8: (1.81617, 2.37566),
            16: (1.80246, 2.3874),
            32: (1.81285, 2.41258),
            64: (1.84162, 2.47155),
            128: (1.90785, 2.58522),
            256: (2.0611, 2.7832),
            512: (2.46074, 3.36588),
            1024: (3.84413, 5.26552),
            2048: (9.9243, 13.9903),
        },
        600000: {
            4: (20.2963, 21.5897),
            8: (20.2442, 21.6206),
            16: (20.1518, 21.6825),
            32: (20.2159, 21.8074),
            64: (20.3957, 22.0614),
            128: (20.7998, 22.5864),
            256: (21.6742, 23.7098),
            512: (23.6222, 25.933),
            1024: (28.3403, 30.2284),
            2048: (40.9191, 44.1259),
        },
    }
    return (claim6_grid,)


@app.cell
def _(claim6_grid, mo):
    batch = mo.ui.dropdown(
        options={f"{value:,}": value for value in claim6_grid},
        value="512",
        label="Claim 6 batch size",
    )
    batch
    return (batch,)


@app.cell
def _(batch, claim6_grid, mo, np, plt):
    _blocks = sorted(claim6_grid[batch.value])
    _pld = [claim6_grid[batch.value][_block][0] for _block in _blocks]
    _rdp = [claim6_grid[batch.value][_block][1] for _block in _blocks]
    _x = np.arange(len(_blocks))
    _fig, _ax = plt.subplots(figsize=(9.0, 4.0))
    _ax.plot(_x, _pld, marker="o", linewidth=2, label="PLD")
    _ax.plot(_x, _rdp, marker="o", linewidth=2, label="RDP")
    _ax.set_xticks(_x, _blocks)
    _ax.set_xlabel("Block size B")
    _ax.set_ylabel("ε at global σ=1")
    _ax.set_title(f"Full-scale Claim 6 slice: batch={batch.value:,}")
    _ax.grid(alpha=0.2)
    _ax.legend(frameon=False)
    _fig.tight_layout()
    _improvements = [
        100 * (_right - _left) / _right
        for _left, _right in zip(_pld, _rdp, strict=True)
    ]
    mo.vstack(
        [
            _fig,
            mo.md(
                f"PLD is tighter at **{len(_blocks)}/{len(_blocks)}** points "
                f"in this slice; improvements range from "
                f"**{min(_improvements):.2f}%** to "
                f"**{max(_improvements):.2f}%**."
            ),
        ]
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Evidence and publication

    This tutorial displays already-produced evidence. It deliberately does not rerun the multi-hour PLD or Monte Carlo experiments. Formal evidence lives in the immutable OpenResearch run logs and committed claim bundles. The cumulative regression passed with all six claim codes equal to zero, and the additive Hugging Face logbook preserves the judged revision.
    """)
    return


if __name__ == "__main__":
    app.run()
