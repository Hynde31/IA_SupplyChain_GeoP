import streamlit as st

st.set_page_config(
    page_title="Supply Chain IA & Géopolitique",
    page_icon=":airplane:",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
# ✈️ Plateforme de Résilience Supply Chain – Airbus & IA

Bienvenue sur la solution de pilotage intelligente de la supply chain face aux risques géopolitiques.

<div style="background: linear-gradient(90deg, #dee2ff 0%, #b5c7f7 100%); padding: 1.2rem; border-radius: 1rem;">
<b>Utilisez le menu de gauche pour accéder :</b>
<ul>
  <li><b>Accueil</b> – Présélection de vos portefeuilles</li>
  <li><b>Dashboard</b> – Cartographie & indicateurs</li>
  <li><b>News géopolitiques</b> – Veille automatique IA</li>
  <li><b>Recommandations IA</b> – Actions stratégiques</li>
</ul>
</div>
""", unsafe_allow_html=True)

st.markdown("""
---
<small>
V.2.0 — UX améliorée, IA & NLP intégrés, visualisation avancée.<br>
Contact : <a href="mailto:contact@airbus.com">contact@airbus.com</a>
</small>
""", unsafe_allow_html=True)
