import streamlit as st

st.set_page_config(page_title="Supply Chain Dashboard", layout="wide")

st.title("Bienvenue sur le Dashboard Supply Chain")
st.write("""
Ce tableau de bord permet de visualiser vos fournisseurs, les zones à risque géopolitique et de suivre vos indicateurs clés de performance supply chain.
""")

# Sélection du portefeuille utilisateur
if "mrp_codes" not in st.session_state:
    st.session_state["mrp_codes"] = []

mrp_input = st.text_input(
    "Entrez vos codes MRP (séparés par des virgules, ex : MRP1,MRP2,MRP3) :",
    value=",".join(st.session_state["mrp_codes"])
)
if st.button("Valider mon portefeuille"):
    st.session_state["mrp_codes"] = [code.strip().upper() for code in mrp_input.split(",") if code.strip()]
    st.success("Portefeuille MRP mis à jour !")

st.write("Utilisez le menu de gauche pour accéder au dashboard et à la veille géopolitique.")
