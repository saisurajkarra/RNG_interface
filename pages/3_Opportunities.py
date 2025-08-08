# # import streamlit as st
# # import pandas as pd
# # from utils.api_fetch import fetch_and_merge_hh_tables
# # from utils.opportunity import classify_opportunity, assign_priority
# # from utils.enrich_gemini import enrich_with_gemini, enrich_facilities_batch

# # st.set_page_config(page_title="Opportunity Enrichment", layout="wide")
# # st.title("📈 Opportunity Enrichment — Landfill Biogas Projects")

# # # --- Data Loading ---
# # @st.cache_data(show_spinner="Loading and merging EPA tables...")
# # def load_data():
# #     df = fetch_and_merge_hh_tables()
# #     if df.empty:
# #         st.error("❌ No data loaded. Please check your network or API.")
# #     return df

# # df = load_data()
# # if df.empty:
# #     st.stop()

# # # --- Region Tagging ---
# # def assign_region(state):
# #     northeast = ['NY', 'NJ', 'PA', 'MA', 'CT', 'RI', 'NH', 'VT', 'ME']
# #     southeast = ['FL', 'GA', 'SC', 'NC', 'AL', 'MS', 'TN', 'KY', 'VA', 'WV', 'AR']
# #     midwest = ['IL', 'IN', 'OH', 'MI', 'WI', 'MN', 'IA', 'MO', 'ND', 'SD', 'NE', 'KS']
# #     west = ['CA', 'WA', 'OR', 'NV', 'UT', 'CO', 'AZ', 'NM', 'AK', 'HI', 'ID', 'MT', 'WY']
# #     if state in northeast:
# #         return "Northeast"
# #     elif state in southeast:
# #         return "Southeast"
# #     elif state in midwest:
# #         return "Midwest"
# #     elif state in west:
# #         return "West"
# #     else:
# #         return "Other"

# # df["Opportunity"] = df.apply(classify_opportunity, axis=1)
# # df["Priority"] = df["Opportunity"].apply(assign_priority)
# # df["Region"] = df["state"].apply(assign_region)

# # # --- Filters ---
# # st.sidebar.header("🔎 Filters")
# # regions = st.sidebar.multiselect("Region", options=sorted(df["Region"].unique()), default=[])
# # priorities = st.sidebar.multiselect("Priority", options=["High", "Medium", "Low"], default=[])
# # epc_filter = st.sidebar.text_input("Filter by EPC name (contains)", "")

# # filtered = df.copy()
# # if regions:
# #     filtered = filtered[filtered["Region"].isin(regions)]
# # if priorities:
# #     filtered = filtered[filtered["Priority"].isin(priorities)]
# # if epc_filter:
# #     filtered = filtered[filtered["gas_collection_sys_manufacture"].str.contains(epc_filter, case=False, na=False)]

# # st.success(f"Showing {len(filtered)} filtered opportunity facilities")

# # # --- Display Table ---
# # with st.expander("📊 View Data Table"):
# #     st.dataframe(filtered[[
# #         "facility_name", "state", "Region", "Opportunity", "Priority", "gas_collection_sys_manufacture"
# #     ]], use_container_width=True)

# # # --- Enrichment ---
# # st.subheader("🧠 Enrich Facilities with Gemini AI")

# # # Single enrichment
# # selected_facility = st.selectbox("Choose a facility to enrich", filtered["facility_name"].unique())
# # selected_row = filtered[filtered["facility_name"] == selected_facility].iloc[0]

# # if st.button("🔍 Enrich selected facility"):
# #     result = enrich_with_gemini(selected_row)
# #     st.markdown("#### 🔍 Enrichment Result")
# #     st.info(result)

# # # Batch enrichment
# # st.markdown("---")
# # if st.button("🚀 Enrich Top 10 Filtered Facilities"):
# #     summaries = enrich_facilities_batch(filtered, limit=10)
# #     for i, (index, row) in enumerate(filtered.head(10).iterrows()):
# #         st.markdown(f"### {i+1}. {row['facility_name']} ({row['state']})")
# #         st.success(summaries[i])
# #         st.divider()
# # pages/3_Opportunities.py  –  advanced batch / cache version

# import streamlit as st
# import pandas as pd
# from utils.api_fetch import fetch_and_merge_hh_tables
# from utils.opportunity import classify_opportunity, assign_priority
# from utils.enrich_gemini import enrich_with_gemini, enrich_facilities_batch
# from datetime import datetime
# import io

# st.set_page_config(page_title="Opportunity Enrichment", layout="wide")
# st.title("📈 Opportunity Enrichment — Landfill Biogas Projects")

# # ------------------------------------------------------------------
# # 1️⃣  Load / preprocess EPA data
# # ------------------------------------------------------------------
# @st.cache_data(show_spinner="Loading & merging EPA tables...")
# def load_data():
#     df = fetch_and_merge_hh_tables()
#     df["Opportunity"] = df.apply(classify_opportunity, axis=1)
#     df["Priority"] = df["Opportunity"].apply(assign_priority)
#     return df

# df_raw = load_data()
# if df_raw.empty:
#     st.error("No EPA data returned.")
#     st.stop()

# # Region classifier
# def assign_region(state):
#     groups = {
#         "Northeast": ['NY','NJ','PA','MA','CT','RI','NH','VT','ME'],
#         "Southeast": ['FL','GA','SC','NC','AL','MS','TN','KY','VA','WV','AR'],
#         "Midwest":   ['IL','IN','OH','MI','WI','MN','IA','MO','ND','SD','NE','KS'],
#         "West":      ['CA','WA','OR','NV','UT','CO','AZ','NM','AK','HI','ID','MT','WY'],
#     }
#     for r, lst in groups.items():
#         if state in lst:
#             return r
#     return "Other"

# df_raw["Region"] = df_raw["state"].apply(assign_region)

# # ------------------------------------------------------------------
# # 2️⃣  Sidebar filters + session cache initialisation
# # ------------------------------------------------------------------
# st.sidebar.header("🔎 Filters")
# region_sel   = st.sidebar.selectbox("Region", ["All"] + sorted(df_raw["Region"].unique()))
# state_sel    = st.sidebar.multiselect("State filter", options=sorted(df_raw["state"].dropna().unique()))
# prio_sel     = st.sidebar.multiselect("Priority", ["High","Medium","Low"], default=["High","Medium","Low"])
# epc_filter   = st.sidebar.text_input("EPC contains")

# filtered = df_raw.copy()
# if region_sel != "All":
#     filtered = filtered[filtered["Region"] == region_sel]
# if state_sel:
#     filtered = filtered[filtered["state"].isin(state_sel)]
# if prio_sel:
#     filtered = filtered[filtered["Priority"].isin(prio_sel)]
# if epc_filter:
#     filtered = filtered[filtered["gas_collection_sys_manufacture"].str.contains(epc_filter, na=False, case=False)]

# st.success(f"{len(filtered):,} facilities match current filter")

# # Session cache: keys "enriched_ids" and "enriched_records"
# if "enriched_ids" not in st.session_state:
#     st.session_state.enriched_ids = set()
# if "enriched_records" not in st.session_state:
#     st.session_state.enriched_records = []

# # ------------------------------------------------------------------
# # 3️⃣  Upload previous metrics to extend cache
# # ------------------------------------------------------------------
# with st.sidebar.expander("⬆️ Upload previous CSV (optional)"):
#     up = st.file_uploader("Load earlier enrichment file", type="csv")
#     if up:
#         prev = pd.read_csv(up)
#         added_ids = set(prev["facility_id"])
#         st.session_state.enriched_ids.update(added_ids)
#         # keep only text field
#         for _, r in prev.iterrows():
#             st.session_state.enriched_records.append(r.to_dict())
#         st.success(f"Merged {len(added_ids)} previously enriched sites into cache")

# # ------------------------------------------------------------------
# # 4️⃣  Show next-30 queue and run enrichment
# # ------------------------------------------------------------------
# BATCH_SIZE = 30
# queue = filtered[~filtered["facility_id"].isin(st.session_state.enriched_ids)].head(BATCH_SIZE)

# st.write(f"**Next batch:** {len(queue)} facilities (will enrich up to {BATCH_SIZE})")
# st.dataframe(queue[["facility_name","state","Priority","gas_collection_sys_manufacture"]])

# if queue.empty:
#     st.info("Nothing new left for this filter. Adjust filters or upload/reset cache.")
# else:
#     if st.button("🚀 Enrich this batch"):
#         summaries = enrich_facilities_batch(queue, limit=len(queue))
#         for row, text in zip(queue.to_dict(orient="records"), summaries):
#             row["gemini_summary"] = text
#             st.session_state.enriched_records.append(row)
#             st.session_state.enriched_ids.add(row["facility_id"])
#         st.success("Batch enrichment complete!")

# # ------------------------------------------------------------------
# # 5️⃣  Metrics + Download current results
# # ------------------------------------------------------------------
# st.sidebar.markdown("---")
# st.sidebar.metric("Cached summaries", f"{len(st.session_state.enriched_records):,}")

# def to_csv(records):
#     return pd.DataFrame(records).to_csv(index=False).encode()

# if st.session_state.enriched_records:
#     st.sidebar.download_button(
#         label="📥 Download CSV",
#         data=to_csv(st.session_state.enriched_records),
#         file_name=f"AL_RNG_enrichment_{datetime.utcnow():%Y%m%d_%H%M}.csv",
#         mime="text/csv",
#     )

# # ------------------------------------------------------------------
# # 6️⃣  Optional clear cache
# # ------------------------------------------------------------------
# with st.sidebar.expander("⚠️ Cache tools"):
#     if st.button("Clear enrichment cache"):
#         st.session_state.enriched_ids.clear()
#         st.session_state.enriched_records.clear()
#         st.success("Cache cleared.")
# pages/3_Opportunities.py
# -----------------------------------------------------------
# Batch + ad-hoc enrichment with persistent summaries
# -----------------------------------------------------------

import streamlit as st
import pandas as pd
from datetime import datetime
from utils.api_fetch   import fetch_and_merge_hh_tables
from utils.opportunity import classify_opportunity, assign_priority
from utils.enrich_gemini import enrich_with_gemini, enrich_facilities_batch

st.set_page_config(page_title="Opportunity Enrichment", layout="wide")
st.title("📈 Opportunity Enrichment — Landfill Biogas Projects")

# ───────────────────────────────────────────────────────────
# 1 Load + preprocess (cached)
# ───────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading & merging EPA tables...")
def load_data():
    df = fetch_and_merge_hh_tables()
    df["Opportunity"] = df.apply(classify_opportunity, axis=1)
    df["Priority"]    = df["Opportunity"].apply(assign_priority)
    return df

df_raw = load_data()
if df_raw.empty:
    st.error("No EPA data returned."); st.stop()

# Region helper
def assign_region(state):
    groups = {
        "Northeast": ['NY','NJ','PA','MA','CT','RI','NH','VT','ME'],
        "Southeast": ['FL','GA','SC','NC','AL','MS','TN','KY','VA','WV','AR'],
        "Midwest"  : ['IL','IN','OH','MI','WI','MN','IA','MO','ND','SD','NE','KS'],
        "West"     : ['CA','WA','OR','NV','UT','CO','AZ','NM','AK','HI','ID','MT','WY'],
    }
    for r, lst in groups.items():
        if state in lst: return r
    return "Other"

df_raw["Region"] = df_raw["state"].apply(assign_region)

# ───────────────────────────────────────────────────────────
# 2 Sidebar filters
# ───────────────────────────────────────────────────────────
st.sidebar.header("🔎 Filters")
region_sel = st.sidebar.selectbox("Region", ["All"] + sorted(df_raw["Region"].unique()))
state_sel  = st.sidebar.multiselect("State filter", sorted(df_raw["state"].dropna().unique()))
prio_sel   = st.sidebar.multiselect("Priority", ["High","Medium","Low","Very-Low","Least"], 
                                    default=["High","Medium","Low"])
epc_filter = st.sidebar.text_input("EPC contains")

filtered = df_raw.copy()
if region_sel != "All":
    filtered = filtered[filtered["Region"] == region_sel]
if state_sel:
    filtered = filtered[filtered["state"].isin(state_sel)]
if prio_sel:
    filtered = filtered[filtered["Priority"].isin(prio_sel)]
if epc_filter:
    filtered = filtered[filtered["gas_collection_sys_manufacture"]
                        .str.contains(epc_filter, na=False, case=False)]

st.success(f"{len(filtered):,} facilities match current filter")

# ───────────────────────────────────────────────────────────
# 3 Session caches
# ───────────────────────────────────────────────────────────
st.session_state.setdefault("enriched_ids", set())
st.session_state.setdefault("enriched_records", [])
st.session_state.setdefault("view_summaries", [])      # NEW ▶ for ad-hoc cards

# ───────────────────────────────────────────────────────────
# 4 CSV import to extend cache
# ───────────────────────────────────────────────────────────
with st.sidebar.expander("⬆️ Upload previous CSV (optional)"):
    up = st.file_uploader("Load earlier enrichment file", type="csv")
    if up:
        prev = pd.read_csv(up)
        st.session_state.enriched_ids.update(prev["facility_id"])
        st.session_state.enriched_records.extend(prev.to_dict("records"))
        st.success(f"Merged {len(prev)} rows")

# ───────────────────────────────────────────────────────────
# 5 Batch-enrich next 30
# ───────────────────────────────────────────────────────────
BATCH_SIZE = 30
queue = filtered[~filtered["facility_id"].isin(st.session_state.enriched_ids)].head(BATCH_SIZE)

st.write(f"**Next batch:** {len(queue)} facilities (max {BATCH_SIZE})")
st.dataframe(queue[["facility_name","state","Priority"]])

if not queue.empty and st.button("🚀 Enrich this batch"):
    texts = enrich_facilities_batch(queue, limit=len(queue))
    for rec, txt in zip(queue.to_dict("records"), texts):
        rec["gemini_summary"] = txt
        st.session_state.enriched_records.append(rec)
        st.session_state.enriched_ids.add(rec["facility_id"])
    st.success("Batch enrichment done!")

# ───────────────────────────────────────────────────────────
# 6 NEW ▶  Ad-hoc multiselect (up to 5) + instant enrich
# ───────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("🎯 Instant enrichment (select up to 5)")

choices = st.multiselect(
    "Choose facilities", 
    options=filtered["facility_name"].unique(), 
    max_selections=5
)

if st.button("✨ Instant Enrich", disabled=len(choices)==0):
    sel_rows = filtered[filtered["facility_name"].isin(choices)]
    for _, r in sel_rows.iterrows():
        fid = r["facility_id"]

    # skip if a card with the same fid is already present
        if any(card.get("fid") == fid for card in st.session_state.view_summaries):
            continue

        # ---------- fetch (from cache or Gemini) ----------
        if fid in st.session_state.enriched_ids:
            summary = next(rec["gemini_summary"]
                        for rec in st.session_state.enriched_records
                        if rec["facility_id"] == fid)
        else:
            summary = enrich_with_gemini(r)
            rec = r.to_dict(); rec["gemini_summary"] = summary
            st.session_state.enriched_records.append(rec)
            st.session_state.enriched_ids.add(fid)

    # ---------- add card with fid so future checks work ----------
        st.session_state.view_summaries.append({
            "fid" : fid,
            "name": r["facility_name"],
            "state": r["state"],
            "text": summary,
        })

# ───────────────────────────────────────────────────────────
# 7 NEW ▶  Show pretty summaries as expanders
# ───────────────────────────────────────────────────────────
if st.session_state.view_summaries:
    st.markdown("## 📝 Instant Enrichment Results")
    for card in st.session_state.view_summaries[::-1]:     # newest first
        with st.expander(f"{card['name']} ({card['state']})", expanded=False):
            st.write(card["text"])

# ───────────────────────────────────────────────────────────
# 8 Metrics + CSV download
# ───────────────────────────────────────────────────────────
st.sidebar.metric("Cached summaries", len(st.session_state.enriched_records))

def _to_csv(recs): return pd.DataFrame(recs).to_csv(index=False).encode()

if st.session_state.enriched_records:
    st.sidebar.download_button(
        "📥 Download CSV",
        data=_to_csv(st.session_state.enriched_records),
        file_name=f"AL_RNG_enrichment_{datetime.utcnow():%Y%m%d_%H%M}.csv",
        mime="text/csv"
    )

# ───────────────────────────────────────────────────────────
# 9 Cache tools
# ───────────────────────────────────────────────────────────
with st.sidebar.expander("🧹 Cache tools"):
    if st.button("Clear all caches"):
        st.session_state.enriched_ids.clear()
        st.session_state.enriched_records.clear()
        st.session_state.view_summaries.clear()
        st.success("Cache cleared")
