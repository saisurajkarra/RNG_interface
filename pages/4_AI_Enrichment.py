import streamlit as st
from utils.enrich_gemini import enrich_with_gemini
from utils.data_cache import update_cached_lead


st.title("AI-Powered Company Intelligence")
name = st.text_input("Company or Facility Name")
city = st.text_input("City")
state = st.text_input("State")

if st.button("Enrich"):
    result = enrich_with_gemini(name, city, state)
    st.text_area("Enrichment Result", result, height=400)
    if st.button("Save to Leads"):
        update_cached_lead(name, result)
        st.success("Lead saved.")