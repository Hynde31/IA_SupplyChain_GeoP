import streamlit as st
import pandas as pd
import pydeck as pdk
from geo_zones import ZONES_GEO

# Mapping code technique -> code affiché
MRP_LABELS = {
    "MRP1": "HEL",
    "MRP2": "EBE",
    "MRP3": "DWI"
}

st.set_page_config(page_title="Dashboard Supply Chain", layout="wide")

mrp_codes = st.session_state.get("mrp_codes", [])
mrp_labels = [MRP_LABELS.get(code, code) for code in mrp_codes]

if not mrp_codes:
    st.warning("Vous devez d'abord définir votre portefeuille MRP sur la page Accueil.")
    st.stop()

@st.cache_data
def load_suppliers(path="mapping_fournisseurs.csv"):
    df = pd.read_csv(path)
    df["Portefeuille"] = df["Portefeuille"].str.upper().str.strip()
    df["Site prod"] = df.get("Site prod", pd.Series("-")).fillna("-")
    df["Pièce"] = df.get("Pièce", pd.Series("-")).fillna("-")
    df["Fournisseur"] = df.get("Fournisseur", pd.Series("-")).fillna("-")
    df["Pays"] = df.get("Pays", pd.Series("-")).fillna("-")
    df["Ville"] = df.get("Ville", pd.Series("-")).fillna("-")
    return df

df_sup = load_suppliers()
df_sup_filtered = df_sup[df_sup["Portefeuille"].isin(mrp_codes)].copy()
df_sup_filtered["Nom Portefeuille"] = df_sup_filtered["Portefeuille"].map(MRP_LABELS)

# ... (le reste du code pour la carte, les KPIs, le tableau...)

# Pour la table finale :
st.header("Vision Approvisionneur : Statuts MRP / Fournisseurs")
st.dataframe(
    df_sup_filtered[
        ["Nom Portefeuille", "Pièce", "Fournisseur", "Site prod", "Pays", "Ville"]
    ].rename(columns={"Nom Portefeuille": "Portefeuille"}),
    use_container_width=True,
    hide_index=True
)
