# utils/enrich_gemini.py

import streamlit as st
import pandas as pd
import time
import google.generativeai as genai  # ✅ correct module

# Configure with API Key
genai.configure(api_key=st.secrets["gemini"]["api_key"])

# Load model
model = genai.GenerativeModel("gemini-2.0-flash")  # You can use gemini-1.5-pro or gemini-1.0-pro too

# Prompt Builder
def sanitize(val):
    return "None" if pd.isna(val) else str(val)


def build_facility_prompt(row: pd.Series) -> str:
    """Craft a prompt that only injects fields actually present in the row."""
    def pick(col, label=None):
        val = row.get(col, None)
        return f"{label or col}: {val}" if pd.notna(val) and val != "" else None

    # ---- assemble lines dynamically ----
    lines = [
        pick("facility_name", "Facility name"),
        pick("city", "City"),
        pick("state", "State"),
        pick("parent_company", "Owner / parent company"),   
        pick("gas_collection_sys_manufacture", "Gas-collection EPC / OEM"),
        pick("passive_vents_or_flares", "Passive vents / flares"),
        pick("annual_modeled_ch4_generation", "Annual modelled CH₄ (tonnes)"),
        pick("landfill_capacity", "Landfill capacity (tons)"),
        pick("is_landfill_open", "Landfill open?"),
        pick("estimated_yr_of_lndfil_closure", "Estimated closure year"),
        pick("reporting_year", "Reporting year"),
    ]

    structured_block = "\n".join([f"• {ln}" for ln in lines if ln])

    return f"""
You are a business-development analyst at Air Liquide Renewable Gas.

EPA DATA
{structured_block}

PRIMARY GOAL → Produce a **LEADS SHEET** with VERIFIED decision-maker contacts.

Steps **(do them silently)**  
1. Search LMOP, state PSC dockets, news, LinkedIn, company sites.  
2. Identify real people who manage the landfill, its gas system, or energy projects.  
3. Give each contact:  name · title · organisation · BEST publicly-available
   link (LinkedIn URL, email, or phone).  
4. Note any EPCs/developers already tied to the site.  
5. List current or planned biogas/RNG activity, grants, PPAs, incentives.  
6. End with crystal-clear BD next steps.

OUTPUT FORMAT (**exactly**):

**Quick Verdict:** <one-line>
**Key Facts**
- …
**Decision-Maker Contacts**
- <Name>, <Title> · <Org> — <LinkedIn/email/phone>
- …
**Competitive Landscape / EPCs**
- …
**Incentives & Permits**
- …
**Next Actions for Air Liquide**
- …

Hyperlink sources whenever possible.  Keep bullets tight; no generic fluff.
"""

# Single Row Enrichment
@st.cache_data(show_spinner=False)
def enrich_with_gemini(row):
    prompt = build_facility_prompt(row)
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Gemini enrichment failed: {e}"

# Batch Enrichment (Top 10)
@st.cache_data(show_spinner=True)
def enrich_facilities_batch(df, limit=10):
    rows = df.head(limit).to_dict(orient="records")
    summaries = []
    progress = st.progress(0)

    for i, row in enumerate(rows):
        try:
            prompt = build_facility_prompt(row)
            response = model.generate_content(prompt)
            summaries.append(response.text.strip())
        except Exception as e:
            summaries.append(f"⚠️ Error: {e}")
        progress.progress((i + 1) / limit)
        time.sleep(1.2)

    return summaries
