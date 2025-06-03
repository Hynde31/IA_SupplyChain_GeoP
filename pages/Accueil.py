import streamlit as st

st.set_page_config(page_title="Accueil", layout="wide")
st.title("Accueil – Saisissez votre portefeuille fournisseur (MRP code)")

st.markdown("""
Pour accéder à votre dashboard personnalisé, entrez un ou plusieurs codes MRP (identifiants SAP de vos articles ou familles fournisseurs).
""")

def go_to_dashboard():
    if st.session_state.get("mrp_input", "").strip():
        st.session_state["mrp_codes"] = [
            code.strip().upper()
            for code in st.session_state["mrp_input"].split(",")
            if code.strip()
        ]
        st.switch_page("pages/Dashboard.py")

st.text_input(
    "Entrez un ou plusieurs codes MRP (séparés par virgule)",
    key="mrp_input",
    on_change=go_to_dashboard
)

if st.button("Valider"):
    go_to_dashboard()

# Optionnel : bouton pour passer à la page suivante même sans saisie valide
if st.button("Page suivante ➡️"):
    st.switch_page("pages/Dashboard.py")
