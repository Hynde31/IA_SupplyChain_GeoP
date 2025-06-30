import streamlit as st
import pandas as pd

st.set_page_config(page_title="Supply Chain Dashboard", layout="wide")

st.title("Bienvenue sur le Dashboard Supply Chain")
st.write("""
Ce tableau de bord permet de visualiser vos fournisseurs, les zones à risque géopolitique et de suivre vos indicateurs clés de performance supply chain.
""")

# Chargement du CSV pour extraire les codes MRP valides
@st.cache_data
def get_mrp_codes(path="mapping_fournisseurs.csv"):
    try:
        df = pd.read_csv(path)
        return sorted(list(df["Portefeuille"].str.upper().str.strip().dropna().unique()))
    except Exception as e:
        st.error(f"Erreur lors du chargement des portefeuilles : {e}")
        return []

valid_mrp_codes = get_mrp_codes()

if not valid_mrp_codes:
    st.error("Aucun portefeuille MRP trouvé dans le fichier CSV. Merci de vérifier votre fichier.")
    st.stop()

# Récupérer la sélection précédente, mais ne garder que les valeurs valides
default_selection = [
    code for code in st.session_state.get("mrp_codes", valid_mrp_codes[:1])
    if code in valid_mrp_codes
]

selection = st.multiselect(
    "Sélectionnez vos codes MRP à suivre :",
    options=valid_mrp_codes,
    default=default_selection
)

if st.button("Valider mon portefeuille"):
    st.session_state["mrp_codes"] = selection
    st.success(f"Portefeuille MRP mis à jour : {', '.join(selection)}")

if "mrp_codes" not in st.session_state:
    st.session_state["mrp_codes"] = default_selection

st.write("Utilisez le menu de gauche pour accéder au dashboard et à la veille géopolitique.")
