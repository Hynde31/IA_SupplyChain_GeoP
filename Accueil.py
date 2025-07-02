import streamlit as st
import pandas as pd

st.set_page_config(page_title="Accueil - Résilience Supply Chain", layout="wide")

@st.cache_data
def load_suppliers(path="mapping_fournisseurs.csv"):
    try:
        # D'abord on tente avec virgule
        df = pd.read_csv(path).fillna("")
        # Si une seule colonne, on essaie avec point-virgule (cas Excel FR)
        if len(df.columns) == 1:
            df = pd.read_csv(path, sep=';').fillna("")
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier : {e}")
        return pd.DataFrame()

df = load_suppliers()

st.title("🏠 Accueil - Résilience Supply Chain Airbus")

# Affiche les colonnes lues et les premières données
st.write("Colonnes détectées :", df.columns.tolist())
if not df.empty:
    st.dataframe(df.head())
else:
    st.warning("Le fichier CSV est vide ou introuvable.")
    st.stop()

# Vérifie présence de la colonne Portefeuille
col_portefeuille = None
for col in df.columns:
    if col.strip().lower() == "portefeuille":
        col_portefeuille = col
        break

if not col_portefeuille:
    st.error("La colonne 'Portefeuille' est absente ou mal nommée dans le fichier CSV.")
    st.stop()

# Charge les MRP codes
mrp_codes = df[col_portefeuille].dropna().unique()

if len(mrp_codes) == 0:
    st.warning("Aucun portefeuille MRP trouvé dans le fichier CSV.")
else:
    selected = st.multiselect("Sélectionnez un ou plusieurs portefeuilles MRP :", mrp_codes)
    if selected:
        st.session_state["mrp_codes"] = selected
        st.success("Sélection enregistrée. Vous pouvez consulter le Dashboard.")
