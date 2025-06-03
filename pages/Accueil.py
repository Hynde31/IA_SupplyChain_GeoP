import streamlit as st

st.set_page_config(page_title="Accueil", layout="wide")
st.title("Accueil – Saisissez votre portefeuille fournisseur (MRP code)")

st.markdown("""
Pour accéder à votre dashboard personnalisé, entrez un ou plusieurs codes MRP (identifiants SAP de vos articles ou familles fournisseurs).
""")

# Saisie : le key doit être fixé pour session_state
mrp_input = st.text_input(
    "Entrez un ou plusieurs codes MRP (séparés par virgule)",
    key="mrp_input"
)

# Si validation par bouton ou entrée (on_change), on stocke et la page va rediriger au prochain run
if st.button("Valider") or (mrp_input and 'mrp_codes' not in st.session_state and st.session_state["mrp_input"].strip()):
    st.session_state["mrp_codes"] = [
        code.strip().upper()
        for code in st.session_state["mrp_input"].split(",")
        if code.strip()
    ]
    st.experimental_rerun()  # Force le reload pour activer la redirection ci-dessous

# Si le portefeuille est saisi, on redirige
if "mrp_codes" in st.session_state:
    st.switch_page("pages/Dashboard.py")

# Optionnel : bouton pour forcer la page suivante même sans MRP (pour test/accès direct)
if st.button("Page suivante ➡️"):
    st.switch_page("pages/Dashboard.py")
