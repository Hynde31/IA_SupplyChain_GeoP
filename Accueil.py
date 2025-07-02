import streamlit as st
import pandas as pd
from suppliers_data import load_suppliers

st.title("AIRBUS - Résilience Supply Chain")

# Chargement des données
suppliers = load_suppliers()

# Filtres
mrp = st.selectbox("Sélectionnez un MRP Code", options=suppliers["MRP Code"].unique())
cat = st.selectbox("Sélectionnez une catégorie", options=suppliers["Category"].unique())

filtered = suppliers[(suppliers["MRP Code"] == mrp) & (suppliers["Category"] == cat)]

st.subheader("Fournisseurs filtrés")
st.dataframe(filtered)

st.markdown("📌 Rendez-vous sur le Dashboard pour la cartographie des risques.")
