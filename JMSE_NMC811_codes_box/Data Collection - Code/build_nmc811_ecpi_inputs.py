"""
build_nmc811_ecpi_inputs.py  (2026-06-21)
=========================================
Emit the NMC811 raw-input ECPI CSV for the revamped ecpi_indicator.py
(whole-system beta, GHG math lives in the indicator).  Mirrors the LFP
revamp (LFP/build_lfp_inputs.py ECPI block, methodology note §8) with
NMC811 chemistry.

NMC811 has NO Fe/P precursors (all cathode metals are recovered), so the
only "produced but not recovered" term would be a lithium recipe-excess --
and here LiCO3 mass_prod == mass_recover (no recipe excess in the workbook),
so the circular sum is the recycled credits only.

SOURCES (Data Collection - Code/indicator_input_values.xlsx, sheet
ECPI_indicator) -- every number below is traceable:
  * masses (mass_prod = m_out_linear): the pre-revamp ECPI CSV / workbook
    in-cell table O62-O68; Al is TOTAL Al (cell 11.590 + module/pack 41.480).
  * virgin_ghg  (kg CO2e/kg): workbook R135-R141 (Virgin Material Production
    GHG).  VALIDATION: sum(mass_prod * virgin_ghg) = 2824.18, which matches the
    pre-revamp LCA_emissions_linear (2824.176561) exactly.
  * F_r (recovery efficiency): user table 2026-06-21 -- steel 0.95, Al 0.93,
    Cu 0.96, Co/Ni/Mn 0.84, Li 0.91 (= the PCI F_r values).
  * in_circ (recycled-content inflow): pre-revamp m_in_circular/m_in_virgin
    -> LiCO3 0.10, Al 0.50, Cu 0.32, Co/Ni/Mn 0.10, steel 0.26.
  * cell_frac: cathode/cell materials (LiCO3, Cu, Co/Ni/Mn sulfates) = 1.0;
    steel = 0.0 (structural, direct secondary-steel rate); Al split cell vs
    module/pack = 11.58982922 / 53.0702835 = 0.21838 (rest -> secondary-Al).
  * recycled_ghg_direct: secondary steel 0.6481, secondary (module+pack) Al
    2.3548 kg CO2e/kg (material properties, shared with LFP).
  * fr_on_direct = 1 for steel (F_r multiplies the steel direct rate), else 0.
  * PARAM_collection = 0.90.
  * PARAM_cell_recycling_ghg_per_kg = 2.369147547315619  (workbook S135,
    "Recycling GHG production ... per kg of battery cell recycled").
  * PARAM_cell_mass_kg = 272.9094828  (CI cell_total; workbook note "battery
    cells weight ... 273 kg").
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.normpath(os.path.join(HERE, '..', 'Code', 'ECPI', 'ECPI_indicator_alpha_sum.csv'))

# --- masses (kg): mass_recover (in-cell recoverable) == mass_prod (production) ---
m = {
    'LiCO3':     41.33697887445953,
    'copper':    33.70028737243632,
    'aluminium': 53.0702835,          # TOTAL Al (cell 11.58982922 + pack 41.48045428)
    'steel':     99.7861565,
    'CoSO4':     17.34532163065482,
    'NiSO4':     138.5423665694946,
    'MnSO4':     16.89677308507337,
}
virgin_ghg = {   # workbook R135-R141
    'LiCO3': 11.82838, 'copper': 3.85988, 'aluminium': 14.36954, 'steel': 2.96911,
    'CoSO4': 6.08086, 'NiSO4': 7.41791, 'MnSO4': 0.77574,
}
F_r = {   # user table 2026-06-21
    'LiCO3': 0.91, 'copper': 0.96, 'aluminium': 0.93, 'steel': 0.95,
    'CoSO4': 0.84, 'NiSO4': 0.84, 'MnSO4': 0.84,
}
in_circ = {   # pre-revamp m_in_circular / m_in_virgin
    'LiCO3': 0.10, 'copper': 0.32, 'aluminium': 0.50, 'steel': 0.26,
    'CoSO4': 0.10, 'NiSO4': 0.10, 'MnSO4': 0.10,
}
AL_CELL_MASS = 11.58982922035457
AL_CELL_FRAC = AL_CELL_MASS / m['aluminium']          # 0.21838...
cell_frac = {
    'LiCO3': 1.0, 'copper': 1.0, 'aluminium': AL_CELL_FRAC, 'steel': 0.0,
    'CoSO4': 1.0, 'NiSO4': 1.0, 'MnSO4': 1.0,
}
rec_direct   = {'aluminium': 2.3548, 'steel': 0.6481}  # secondary Al / steel (kg CO2e/kg)
fr_on_direct = {'steel': 1}

COLLECTION                 = 0.90
CELL_RECYCLING_GHG_PER_KG  = 2.369147547315619         # workbook S135
CELL_MASS_KG               = 272.9094828               # CI cell_total

ORDER = ['LiCO3', 'copper', 'aluminium', 'steel', 'CoSO4', 'NiSO4', 'MnSO4']


def build():
    rows = [['material', 'mass_recover', 'mass_prod', 'virgin_ghg', 'F_r', 'in_circ',
             'cell_frac', 'recycled_ghg_direct', 'fr_on_direct']]
    for k in ORDER:
        rows.append([k, m[k], m[k], virgin_ghg[k], F_r[k], in_circ[k],
                     cell_frac[k], rec_direct.get(k, ''), fr_on_direct.get(k, 0)])
    rows.append(['PARAM_collection',                COLLECTION,                '', '', '', '', '', '', ''])
    rows.append(['PARAM_cell_recycling_ghg_per_kg', CELL_RECYCLING_GHG_PER_KG, '', '', '', '', '', '', ''])
    rows.append(['PARAM_cell_mass_kg',              CELL_MASS_KG,              '', '', '', '', '', '', ''])
    with open(OUT, 'w', newline='', encoding='utf-8') as f:
        csv.writer(f).writerows(rows)

    linear = sum(m[k] * virgin_ghg[k] for k in ORDER)
    print(f"Wrote {OUT}")
    print(f"  sum(mass_prod * virgin_ghg) = {linear:.4f}  (pre-revamp linear = 2824.1766; match -> inputs OK)")
    print(f"  Al cell_frac = {AL_CELL_FRAC:.5f}  (pack Al = {m['aluminium']-AL_CELL_MASS:.4f} kg)")


if __name__ == '__main__':
    build()
