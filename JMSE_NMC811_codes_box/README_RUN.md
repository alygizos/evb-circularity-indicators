# NMC811 Circularity Indicators — how to run

This box is **self-contained**: no files outside it are needed at runtime.

## Setup
```
pip install -r requirements.txt        # Python 3.12 recommended
```

## Layout
- `Code/PCI, CI, CEI, ECPI, MRE/` — the five indicator scripts, each reading a local
  input CSV in its own folder.
- `Code/cumulative_results_indicators.csv` — shared results cache (each indicator writes
  its own row).
- `Code/compiled_results_indicator.py` — reads the cache, draws the comparison figure.
- `Code/sensitivity/nmc811_sensitivity_lite.py` — recomputes the S1/S2/S3 studies,
  writing `S{1,2,3}_sensitivity_study.csv` + comparison PNGs.
- `Data Collection - Code/` — source workbooks + `build_nmc811_ecpi_inputs.py`
  (regenerates the ECPI raw-input CSV). Source data only; not needed to run the indicators.

## Run the indicators (each writes its plots + its row in the cumulative CSV)
Run from inside each folder. **MRE must run last** in a batch, because PCI/CI/CEI/ECPI
each rewrite the cumulative CSV keeping only `[PCI, CI, CEI, ECPI]`; only MRE adds `M,R,E`:
```
cd Code/PCI  && python pci_indicator_v2.py
cd ../CI     && python ci_indicator.py
cd ../CEI    && python cei_indicator.py
cd ../ECPI   && python ecpi_indicator.py
cd ../MRE    && python mre_indicator.py
cd ..        && python compiled_results_indicator.py
```

## Run the sensitivity studies
```
cd Code/sensitivity
python nmc811_sensitivity_lite.py            # writes S1/S2/S3 CSV tables + comparison PNGs, then restores base
python nmc811_sensitivity_lite.py --restore-base   # just rebuild the clean base case
```

## Regenerate the ECPI raw-input CSV (optional)
```
cd "Data Collection - Code"
python build_nmc811_ecpi_inputs.py           # rewrites Code/ECPI/ECPI_indicator_alpha_sum.csv
```

## Notes
- The indicator scripts call `plt.show()`; running them interactively pops up figures
  (close them to continue). For headless/batch runs set the backend first:
  `MPLBACKEND=Agg` (the sensitivity engine already does this for its subprocess runs).
- ECPI uses the revamped raw-input / `eq2` method (GHG math is inside `ecpi_indicator.py`).
- `*_PRE_REVAMP.*` and `*_PRE_LITE.*` files are pre-update backups; safe to delete.
- See `CHANGES_vs_MSEC.md` for the full change log.
```
