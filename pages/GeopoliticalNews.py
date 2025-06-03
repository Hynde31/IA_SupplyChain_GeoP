import streamlit as st
from geo_news_nlp import get_news_impact_for_month

st.set_page_config(page_title="Veille géopolitique Supply Chain", layout="wide")
st.title("Veille géopolitique et détection d'impacts Supply Chain")

mois = st.selectbox("Sélectionnez le mois à analyser", [
    "2025-06", "2025-05", "2025-04", "2025-03", "2025-02", "2025-01"
])

if st.button("Lancer l'analyse"):
    with st.spinner("Chargement des actualités, analyse NLP et géocodage..."):
        news, impacts = get_news_impact_for_month(mois)
    st.success(f"{len(news)} actualités trouvées pour {mois}")

    st.subheader("Liste des actualités")
    for n in news:
        st.markdown(f"- **{n['date']}** : **{n['title']}**<br>{n['summary']}", unsafe_allow_html=True)

    st.subheader("Impacts géopolitiques détectés (zones géographiques)")
    if impacts:
        st.dataframe([
            {
                "Zone": imp["zone"],
                "Latitude": imp["lat"],
                "Longitude": imp["lon"],
                "Impact": imp["impact"]
            } for imp in impacts
        ])
        st.map(
            data={
                "lat": [imp["lat"] for imp in impacts],
                "lon": [imp["lon"] for imp in impacts]
            }
        )
    else:
        st.info("Aucun impact géopolitique détecté pour ce mois.")
else:
    st.info("Cliquez sur le bouton ci-dessus pour lancer l'analyse.")

# Navigation boutons
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("⬅️ Dashboard"):
        st.switch_page("pages/Dashboard.py")
with col2:
    if st.button("🏠 Accueil"):
        st.switch_page("pages/Accueil.py")
