import streamlit as st
from geo_news_nlp import get_news_impact_for_month

st.set_page_config(page_title="Veille géopolitique Supply Chain", layout="wide")
st.title("Veille géopolitique et détection d'impacts Supply Chain")

# Sélection de la période (année/mois)
mois = st.selectbox("Sélectionnez le mois à analyser", [
    "2025-06", "2025-05", "2025-04", "2025-03", "2025-02", "2025-01"
])

# Lancer l'analyse avec un bouton
if st.button("Lancer l'analyse"):
    with st.spinner("Chargement des actualités, analyse NLP et géocodage..."):
        news, impacts = get_news_impact_for_month(mois)
    st.success(f"{len(news)} actualités trouvées pour {mois}")

    # Affichage des actualités
    st.subheader("Liste des actualités")
    for n in news:
        st.markdown(f"- **{n['date']}** : **{n['title']}**<br>{n['summary']}", unsafe_allow_html=True)

    # Affichage des impacts géopolitiques détectés
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
        # Carte si au moins un impact
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
