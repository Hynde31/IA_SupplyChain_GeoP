import streamlit as st

st.title("Accueil")
st.write("""
Bienvenue sur la page d'accueil du dashboard Supply Chain.  
Utilisez le menu de gauche pour naviguer vers le tableau de bord principal ou la veille géopolitique.
""")
st.page_link("app.py", label="🔙 Retour page principale")
