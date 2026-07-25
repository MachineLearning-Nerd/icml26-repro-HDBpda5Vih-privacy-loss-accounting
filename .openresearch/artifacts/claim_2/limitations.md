# Limitations and deviations

Asymptotic Big-O cannot be proven by finite timing. The gate therefore uses the
released operation structure and primitive pair-product counts as its primary
complexity evidence; wall time is recorded but not used as a brittle pass
condition. Exact accuracy checks use finite four-atom inputs. The Gaussian API
checks cover t up to 256 rather than the paper's largest application and use
coarse alpha values so this branch remains a targeted CPU contract test.
