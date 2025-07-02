import streamlit as st
import pandas as pd

st.set_page_config(page_title="Accueil - Résilience Supply Chain", layout="wide")

@st.cache_data
def load_suppliers(path="mapping_fournisseurs.csv"):
    try:
        df = pd.read_csv(path).fillna("")
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier : {e}")
        return pd.DataFrame()

df = load_suppliers()

st.title("🏠 Accueil - Résilience Supply Chain Airbus")

st.write("Colonnes détectées :", df.columns.tolist())
st.dataframe(df)

if df.empty:
    st.warning("Aucun portefeuille MRP trouvé dans le fichier CSV.")
else:
    if "Portefeuille" not in df.columns:
        st.warning("La colonne 'Portefeuille' est absente du fichier CSV.")
    else:
        mrp_codes = df["Portefeuille"].dropna().unique()
        selected = st.multiselect("Sélectionnez un ou plusieurs portefeuilles MRP :", mrp_codes)
        if selected:
            st.session_state["mrp_codes"] = selected
            st.success("Sélection enregistrée. Vous pouvez consulter le Dashboard.")
