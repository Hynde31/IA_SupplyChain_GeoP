import streamlit as st

st.set_page_config(
    page_title="Supply Chain IA & Géopolitique",
    page_icon="🧠🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
# 🧠🌍 Plateforme de Résilience Supply Chain

Bienvenue sur la plateforme de pilotage intelligente dédiée à la résilience de la supply chain aéronautique face aux risques géopolitiques.

Cette solution vous permet d’analyser, visualiser et anticiper les impacts des perturbations mondiales sur votre portefeuille fournisseur.

---
""")

# Section de sélection ou ajout de codes ID
st.markdown("## 🔢 Sélection ou ajout d'un code portefeuille ID")

# Récupérer les codes ID déjà présents en session ou les initialiser
if "ID_codes" not in st.session_state:
    st.session_state["ID_codes"] = []

current_codes = st.session_state["ID_codes"]

# Affichage de la liste actuelle
if current_codes:
    st.markdown("**Codes ID sélectionnés actuellement :**")
    st.write(", ".join(current_codes))
else:
    st.info("Aucun code ID sélectionné pour l'instant.")

# Entrée pour ajouter un nouveau code ID
new_code = st.text_input(
    "Ajouter un code ID (exemple : HEL, EBE, DWI)", 
    max_chars=10, 
    help="Entrez un code portefeuille puis validez pour l'ajouter à votre sélection."
).strip().upper()

if st.button("Ajouter ce code ID"):
    if new_code and new_code not in current_codes:
        st.session_state["ID_codes"].append(new_code)
        st.success(f"Code ID '{new_code}' ajouté !")
    elif not new_code:
        st.warning("Veuillez saisir un code ID avant d'ajouter.")
    else:
        st.info(f"Le code ID '{new_code}' est déjà dans la liste.")

# Option pour réinitialiser la sélection
if st.button("Réinitialiser la sélection des codes ID"):
    st.session_state["ID_codes"] = []
    st.info("Sélection des codes ID réinitialisée.")

# Astuce UX
st.caption("""
*Votre sélection de codes ID personnalise tous les dashboards et analyses de la plateforme. 
Rendez-vous dans le menu Accueil ou Dashboard pour explorer vos données fournisseurs selon vos choix.*
""")
