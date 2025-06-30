import streamlit as st
import pandas as pd

st.set_page_config(page_title="Supply Chain Dashboard", layout="wide")

# Mapping codes internes <-> codes affichés
MRP_LABELS = {
    "MRP1": "HEL",
    "MRP2": "EBE",
    "MRP3": "DWI"
}
MRP_LABELS_INV = {v: k for k, v in MRP_LABELS.items()}

st.title("Bienvenue sur le Dashboard Supply Chain")
st.write("""
Ce tableau de bord permet de visualiser vos fournisseurs, les zones à risque géopolitique et de suivre vos indicateurs clés de performance supply chain.
""")

@st.cache_data
def get_mrp_codes(path="mapping_fournisseurs.csv"):
    try:
        df = pd.read_csv(path)
        codes = sorted(list(df["Portefeuille"].str.upper().str.strip().dropna().unique()))
        # On ne garde que ceux présents dans le mapping
        codes = [code for code in codes if code in MRP_LABELS]
        return codes
    except Exception as e:
        st.error(f"Erreur lors du chargement des portefeuilles : {e}")
        return []

valid_mrp_codes = get_mrp_codes()

if not valid_mrp_codes:
    st.error("Aucun portefeuille MRP trouvé dans le fichier CSV. Merci de vérifier votre fichier.")
    st.stop()

# Valeurs affichées = labels
valid_labels = [MRP_LABELS[code] for code in valid_mrp_codes]

# Par défaut, on sélectionne tout ou l'ancienne sélection si encore valide
previous_labels = [
    label for label in st.session_state.get("mrp_labels", valid_labels)
    if label in valid_labels
]

selection = st.multiselect(
    "Sélectionnez vos portefeuilles MRP à suivre :",
    options=valid_labels,
    default=previous_labels
)

if st.button("Valider mon portefeuille"):
    st.session_state["mrp_labels"] = selection
    # On stocke aussi les codes internes pour les autres pages
    st.session_state["mrp_codes"] = [MRP_LABELS_INV[label] for label in selection]
    st.success(f"Portefeuille MRP mis à jour : {', '.join(selection)}")

# Init session_state au premier affichage
if "mrp_labels" not in st.session_state:
    st.session_state["mrp_labels"] = previous_labels
if "mrp_codes" not in st.session_state:
    st.session_state["mrp_codes"] = [MRP_LABELS_INV[label] for label in previous_labels]

st.write("Utilisez le menu de gauche pour accéder au dashboard et à la veille géopolitique.")
