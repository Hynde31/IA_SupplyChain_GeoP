import streamlit as st

st.set_page_config(page_title="Accueil", layout="wide")
st.title("Accueil – Saisissez votre portefeuille fournisseur (MRP code)")

st.markdown("""
Pour accéder à votre dashboard personnalisé, entrez un ou plusieurs codes MRP (identifiants SAP de vos articles ou familles fournisseurs).
""")

def valid_mrp_input():
    if st.session_state["mrp_input"].strip():
        st.session_state["mrp_codes"] = [
            code.strip().upper()
            for code in st.session_state["mrp_input"].split(",")
            if code.strip()
        ]

st.text_input(
    "Entrez un ou plusieurs codes MRP (séparés par virgule)",
    key="mrp_input",
    on_change=valid_mrp_input
)

if st.button("Valider"):
    valid_mrp_input()

# Redirection automatique si un portefeuille est présent
if "mrp_codes" in st.session_state:
    st.switch_page("pages/Dashboard.py")

if st.button("Page suivante ➡️"):
    st.switch_page("pages/Dashboard.py")
