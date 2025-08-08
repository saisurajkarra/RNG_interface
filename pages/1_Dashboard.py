
import streamlit as st
import pandas as pd
from utils.api_fetch   import fetch_and_merge_hh_tables
from utils.opportunity import classify_opportunity, assign_priority

st.set_page_config(page_title="Landfill Dashboard", layout="wide")
st.title("🏭 Landfill Dashboard")

# ───────────────────────────────────────────────────────────
# 1️⃣  One-time data load → cached in session_state
# ───────────────────────────────────────────────────────────
if "full_df" not in st.session_state:
    with st.spinner("Fetching & merging EPA tables …"):
        df = fetch_and_merge_hh_tables()

        # If API failed
        if df.empty:
            st.session_state.full_df = pd.DataFrame()   # avoid repeat calls
        else:
            # classify & add region
            df["Opportunity"] = df.apply(classify_opportunity, axis=1)
            df["Priority"]    = df["Opportunity"].apply(assign_priority)

            try:
                from utils.region_tagging import assign_region
                df["Region"] = df["state"].apply(assign_region)
            except Exception:
                df["Region"] = "Unknown"

            st.session_state.full_df = df

df = st.session_state.full_df
if df.empty:
    st.error("❌ No data available from EPA API.")
    st.stop()

# ───────────────────────────────────────────────────────────
# 2️⃣  Sidebar slider: max NaN columns allowed
# ───────────────────────────────────────────────────────────
st.sidebar.header("ℹ️ Row quality filter")
max_nan = st.sidebar.slider(
    label    ="Max empty (NaN) columns per row",
    min_value=0,
    max_value=len(df.columns),
    value    =15,
    step     =1,
)

filtered = df[df.isna().sum(axis=1) < max_nan]

# ───────────────────────────────────────────────────────────
# 3️⃣  Metrics & table
# ───────────────────────────────────────────────────────────
st.metric("Facilities shown", len(filtered))
st.metric("High-priority leads", (filtered["Priority"] == "High").sum())

with st.expander("📊 Show data table", expanded=True):
    st.dataframe(filtered, use_container_width=True)

# ───────────────────────────────────────────────────────────
# 4️⃣  Optional clear-session button
# ───────────────────────────────────────────────────────────
with st.sidebar.expander("🧹 Data cache tools"):
    if st.button("Reload EPA data (clear cache)"):
        del st.session_state["full_df"]
        st.experimental_rerun()
