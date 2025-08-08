# # def classify_opportunity(row):
# #     manu = str(row.get("gas_collection_sys_manufacture", "")).lower()
# #     if not manu.strip():
# #         return "❗ No EPC"

# #     airliquide_aliases = ["air liquide", "airliquide", "air gas", "air liquide biogas"]
# #     epc_known = ["cdm smith", "waste energy technology", "wet", "scs engineers", "the shaw group", "golder", "golder & associates", "hav"]

# #     if any(ali in manu for ali in airliquide_aliases):
# #         return "✔ Existing Client"
# #     elif any(epc in manu for epc in epc_known):
# #         return f"🔍 EPC: {manu.title()}"
# #     else:
# #         return f"🔍 EPC: {manu.title()}"

# # def assign_priority(opportunity):
# #     if opportunity == '❗ No EPC':
# #         return "High"
# #     elif 'EPC:' in opportunity:
# #         return "Medium"
# #     else:
# #         return "Low"

# # utils/opportunity.py
# # --------------------------------------------------
# # Classify opportunity based on EPC + gas potential.
# # --------------------------------------------------

# import numpy as np
# import pandas as pd

# # ------------------------------- EPC-based tag
# def _epc_tag(manu: str) -> str:
#     manu = str(manu).lower()

#     if not manu.strip():
#         return "❗ No EPC"

#     airliquide_aliases = ["air liquide", "airliquide", "air gas", "air liquide biogas"]
#     epc_known = [
#         "cdm smith", "waste energy technology", "wet",
#         "scs engineers", "the shaw group", "golder",
#         "golder & associates", "hav"
#     ]

#     if any(a in manu for a in airliquide_aliases):
#         return "✔ Existing Client"
#     elif any(e in manu for e in epc_known):
#         return f"🔍 EPC: {manu.title()}"
#     else:
#         return f"🔍 EPC: {manu.title()}"


# # ------------------------------- flow-based score
# def _methane_flow_scfph(row: pd.Series) -> float | None:
#     """
#     Estimate methane flow (scf/h) from EPA fields:
#     - annual_landfill_gas_flow : reported as SCFM (scf/min) *or* scf/yr depending on reporter.
#     - annl_avg_methane_concentration : %, 0-100
#     We assume value is SCFM; multiply by 60 for scf/h and by CH₄ fraction.
#     Returns None if inputs missing/non-numeric.
#     """
#     try:
#         flow_scfm = float(row.get("annual_landfill_gas_flow", np.nan))
#         ch4_frac  = float(row.get("annl_avg_methane_concentration", np.nan)) / 100
#     except Exception:
#         return None

#     if np.isnan(flow_scfm) or np.isnan(ch4_frac):
#         return None

#     return flow_scfm * 60 * ch4_frac   # scf/h of CH₄


# def _flow_priority(flow_scfph: float | None) -> str:
#     if flow_scfph is None:
#         return "Very-Low"
#     if flow_scfph >= 210_000:
#         return "High"
#     if flow_scfph >= 90_000:
#         return "Medium"
#     if flow_scfph >= 48_000:
#         return "Low"
#     return "Very-Low"


# # ------------------------------- public helpers
# def classify_opportunity(row: pd.Series) -> str:
#     """Return a composite tag (EPC tag + numeric potential)."""
#     epc_tag  = _epc_tag(row.get("gas_collection_sys_manufacture", ""))
#     flow_tag = _flow_priority(_methane_flow_scfph(row))
#     return f"{epc_tag} | {flow_tag}"


# def assign_priority(opportunity: str) -> str:
#     """
#     Convert composite tag to Priority.
#     If the incoming string is malformed (no '|') or NaN, treat it as Low.
#     """
#     if not isinstance(opportunity, str) or "|" not in opportunity:
#         # fall-back: treat unrecognised strings as Low priority
#         return "Low"

#     epc_part, flow_part = [p.strip() for p in opportunity.split("|", 1)]

#     # Existing client
#     if epc_part.startswith("✔"):
#         return "Served"

#     # No EPC logic
#     if epc_part.startswith("❗"):
#         if flow_part == "High":
#             return "High"
#         if flow_part == "Medium":
#             return "Medium"
#         return "Low"

#     # Some EPC present (but not AL)
#     if flow_part == "High":
#         return "Medium"
#     if flow_part == "Medium":
#         return "Low"
#     return "Very-Low"


"""
Opportunity tagging + priority scoring
--------------------------------------
 • EPC tag (Existing Client / EPC name / No EPC)
 • Gas-flow band based on annual_landfill_gas_flow * CH₄%
 • Composite string: "<EPC tag> | <FlowBand>"
 • Priority rules tuned per Air Liquide BD

Flow-band thresholds (scf/h methane):

    ≥ 50 000 ....................... High
    25 000 – 49 999 ............... Medium
    10 000 – 24 999 ............... Low
     1 000 –  9 999 ............... Very-Low
       < 1 000  ................... Least
    Missing data .................. Low    (fallback)
"""
# utils/opportunity.py  – flow-only version
# -----------------------------------------------------------
# Classify opportunity & priority strictly by methane flow.
# -----------------------------------------------------------

import numpy as np
import pandas as pd

# ──────────────────────────────
# Methane-flow estimate (scf/h)
# ──────────────────────────────
def _methane_flow_scfph(row: pd.Series) -> float | None:
    """
    annual_landfill_gas_flow  → SCFM
    annl_avg_methane_concentration → %
    Returns scf/h of CH₄, or None if data missing.
    """
    try:
        scfm   = float(row.get("annual_landfill_gas_flow", np.nan))
        ch4pct = float(row.get("annl_avg_methane_concentration", np.nan)) / 100
    except Exception:
        return None

    if np.isnan(scfm) or np.isnan(ch4pct):
        return None

    return scfm * 60 * ch4pct          # scf/h methane

# ──────────────────────────────
# Flow band thresholds
# ──────────────────────────────
def _flow_band(flow: float | None) -> str:
    if flow is None:           return "Unknown"
    if flow >= 1000:         return "High"
    if flow >= 500:         return "Medium"
    if flow >= 50:         return "Low"
    if flow >=  5:         return "Very-Low"
    return "Least"

# ──────────────────────────────
# Public helpers
# ──────────────────────────────
def classify_opportunity(row: pd.Series) -> str:
    """
    Returns just the flow band: High / Medium / Low / Very-Low / Least / Unknown
    """
    return _flow_band(_methane_flow_scfph(row))


def assign_priority(opportunity: str) -> str:
    """
    Map band → Priority (same labels).
    Unknown counts as Low so it appears on maps.
    """
    band = str(opportunity)

    if band == "High":       return "High"
    if band == "Medium":     return "Medium"
    if band == "Low":        return "Low"
    if band == "Very-Low":   return "Very-Low"
    if band == "Least":      return "Least"
    return "Low"             # Unknown / missing
