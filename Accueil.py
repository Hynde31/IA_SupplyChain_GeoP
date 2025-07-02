import streamlit as st
import pandas as pd

@st.cache_data
def load_suppliers(path="mapping_fournisseurs.csv"):
    return pd.read_csv(path).fillna("")

df = load_suppliers()

st.title("🏠 Accueil - Résilience Supply Chain Airbus")

# Sélection des MRP
if "Portefeuille" not in df.columns or df["Portefeuille"].dropna().empty:
    st.warning("Aucun portefeuille MRP trouvé dans le fichier CSV. Merci de vérifier votre fichier.")
else:
    mrp_codes = df["Portefeuille"].dropna().unique()
    selected = st.multiselect("Sélectionnez un ou plusieurs portefeuilles MRP :", mrp_codes)

    if selected:
        st.session_state["mrp_codes"] = selected
        st.success("Sélection enregistrée. Vous pouvez consulter le Dashboard.")
