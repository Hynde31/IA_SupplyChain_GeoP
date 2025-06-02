import streamlit as st

st.set_page_config(page_title="Airbus Supply Risk Suite", layout="wide", initial_sidebar_state="expanded")

st.sidebar.title("Navigation")
st.sidebar.success("Choisissez une page ci-dessus.")

# Utilise la navigation native de Streamlit (pages/) ou ajoute un menu custom si besoin.
st.title("Airbus Supply Risk Suite")
st.markdown("""
Bienvenue sur la plateforme de gestion des risques fournisseurs Airbus.  
Utilisez la barre latérale pour naviguer entre l'accueil (saisie de MRP code), le dashboard du portefeuille, et la veille géopolitique.
""")