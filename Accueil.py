import streamlit as st
import pandas as pd

@st.cache_data
def load_suppliers(path="mapping_fournisseurs.csv"):
    return pd.read_csv(path).fillna("")

df = load_suppliers()
mrp_codes = df["Portefeuille"].dropna().unique()

st.title("🏠 Accueil - Résilience Supply Chain Airbus")

selected = st.multiselect("Sélectionnez un ou plusieurs portefeuilles MRP :", mrp_codes)

if selected:
    st.session_state["mrp_codes"] = selected
    st.success("Sélection enregistrée. Vous pouvez consulter le Dashboard.")
