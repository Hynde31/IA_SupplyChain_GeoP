import streamlit as st

st.set_page_config(page_title="Accueil", layout="wide")
st.title("Bienvenue sur la plateforme de gestion des approvisionnements en fonction des perturbations géopolitiques")

st.markdown("Cliquez pour accéder au dashboard.")
if st.button("Aller au Dashboard ➡️"):
    st.switch_page("pages/Dashboard.py")
