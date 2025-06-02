app.py
/pages
    Accueil.py
    Dashboard.py
    GeopoliticalNews.py

import streamlit as st

st.title("Accueil – Saisissez votre portefeuille fournisseur (MRP code)")

st.markdown("""
Pour accéder à votre dashboard personnalisé, entrez un ou plusieurs codes MRP (identifiants SAP de vos articles ou familles fournisseurs).
""")

mrp_input = st.text_input("Entrez un ou plusieurs codes MRP (séparés par virgule)", "")
if st.button("Valider") and mrp_input.strip():
    st.session_state["mrp_codes"] = [code.strip().upper() for code in mrp_input.split(",") if code.strip()]
    st.success("MRP codes validés. Accédez à la page Dashboard via la navigation à gauche.")
else:
    st.info("Entrez au moins un code MRP pour continuer.")
