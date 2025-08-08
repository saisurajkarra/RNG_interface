import streamlit as st
import pandas as pd


st.title("Saved Sales Leads")
try:
    leads = pd.read_csv("data/sales_leads.csv")
    st.dataframe(leads)
except:
    st.info("No leads saved yet.")
