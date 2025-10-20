import streamlit as st
import pandas as pd

st.set_page_config(page_title="Accueil - Résilience Supply Chain", layout="wide")

@st.cache_data
def load_suppliers(path="mapping_fournisseurs.csv"):
    try:
        df = pd.read_csv(path).fillna("")
        if len(df.columns) == 1:
            df = pd.read_csv(path, sep=';').fillna("")
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier : {e}")
        return pd.DataFrame()

df = load_suppliers()

st.markdown("# 🧠🌍 Plateforme de Résilience Supply Chain")
st.markdown("### Accueil — Sélection de votre portefeuille")
st.caption("""
En tant que supply chain officer ou acheteur, sélectionnez ci-dessous le ou les portefeuilles que vous souhaitez analyser.
La sélection personnalisera l’ensemble des indicateurs et analyses de la plateforme.
""")

if df.empty:
    st.error("Aucune donnée fournisseur trouvée. Merci de vérifier le fichier mapping_fournisseurs.csv.")
    st.stop()

col_portefeuille = next((col for col in df.columns if col.strip().lower() == "portefeuille"), None)
if not col_portefeuille:
    st.error("La colonne 'Portefeuille' est absente ou mal nommée dans le fichier CSV.")
    st.stop()

ID_codes = sorted(df[col_portefeuille].dropna().unique())
if not ID_codes:
    st.warning("Aucun portefeuille détecté.")
    st.stop()

# Sélection centrale et design premium
default_selection = st.session_state.get("ID_codes", ID_codes)
st.markdown("#### Choix du code portefeuille ID")
selected = st.multiselect(
    "Sélectionnez votre portefeuille ID :",
    ID_codes,
    default=default_selection,
    help="Exemple : HEL (électronique), EBE (cabines), etc."
)

col1, col2 = st.columns(2)
with col1:
    if st.button("✅ Valider ma sélection"):
        st.session_state["ID_codes"] = selected
        st.success("Sélection enregistrée ! Toutes les données affichées correspondront à ce portefeuille.")

with col2:
    if st.button("🔄 Réinitialiser"):
        st.session_state["ID_codes"] = ID_codes
        st.info("Sélection réinitialisée.")

# Aperçu dynamique du portefeuille sélectionné
if selected:
    st.markdown("---")
    st.markdown("#### Aperçu de votre portefeuille fournisseur")
    st.dataframe(df[df[col_portefeuille].isin(selected)], use_container_width=True, hide_index=True)
else:
    st.info("Sélectionnez au moins un portefeuille pour voir les fournisseurs associés.")
