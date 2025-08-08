import streamlit as st
import pandas as pd


st.title("Saved Company Contacts")
try:
    df = pd.read_csv("data/enriched_epcs.csv")
    st.dataframe(df)
except:
    st.info("No enriched EPCs yet. Run enrichment first.")