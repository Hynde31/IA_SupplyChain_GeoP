import streamlit as st

st.set_page_config(page_title="Accueil", layout="wide")
st.title("Accueil – Saisissez votre portefeuille fournisseur (MRP code)")

st.markdown("""
Pour accéder à votre dashboard personnalisé, entrez un ou plusieurs codes MRP (identifiants SAP de vos articles ou familles fournisseurs).
""")

def valider_mrp():
    if st.session_state["mrp_input"].strip():
        st.session_state["mrp_codes"] = [code.strip().upper() for code in st.session_state["mrp_input"].split(",") if code.strip()]
        st.switch_page("pages/Dashboard.py")

st.text_input(
    "Entrez un ou plusieurs codes MRP (séparés par virgule)",
    key="mrp_input",
    on_change=valider_mrp
)

if st.button("Valider"):
    valider_mrp()

# Bouton page suivante (Dashboard) même si pas validé
if st.button("Page suivante ➡️"):
    st.switch_page("pages/Dashboard.py")
