import streamlit as st

st.set_page_config(page_title="Veille géopolitique Supply Chain", layout="wide")
st.title("Veille géopolitique et détection d'impacts Supply Chain")

months = [f"2025-{m:02}" for m in range(1, 13)]

NLP_AVAILABLE = True
msg = ""
try:
    from geo_news_nlp import get_news_impact_for_month
except ImportError:
    try:
        import spacy
        spacy.load("fr_core_news_sm")
    except Exception:
        try:
            spacy.load("en_core_web_sm")
            msg = "Le modèle spaCy 'fr_core_news_sm' n'est pas disponible, passage à l'anglais."
        except Exception:
            NLP_AVAILABLE = False
            msg = ("Aucun modèle spaCy compatible n'a pu être chargé. Les fonctionnalités de veille géopolitique sont désactivées.")

if not NLP_AVAILABLE:
    st.error(msg)
else:
    if msg:
        st.warning(msg)
    mois = st.selectbox("Sélectionnez le mois à analyser", months)
    if st.button("Lancer l'analyse"):
        with st.spinner("Chargement des actualités, analyse NLP et géocodage..."):
            news, impacts = get_news_impact_for_month(mois)
        if news is not None and len(news) > 0:
            st.success(f"{len(news)} actualités trouvées pour {mois}")
            st.subheader("Liste des actualités")
            for n in news:
                st.markdown(f"- **{n['date']}** : **{n['title']}**<br>{n['summary']}", unsafe_allow_html=True)
        else:
            st.info("Aucune actualité trouvée ou analyse impossible.")

        st.subheader("Impacts géopolitiques détectés (zones géographiques)")
        if impacts and len(impacts) > 0:
            st.dataframe([
                {
                    "Zone": imp.get("zone", ""),
                    "Latitude": imp.get("lat", ""),
                    "Longitude": imp.get("lon", ""),
                    "Impact": imp.get("impact", "")
                } for imp in impacts
            ])
            st.map(
                data={
                    "lat": [imp.get("lat") for imp in impacts],
                    "lon": [imp.get("lon") for imp in impacts]
                }
            )
        else:
            st.info("Aucun impact géopolitique détecté pour ce mois.")
    else:
        st.info("Cliquez sur le bouton ci-dessus pour lancer l'analyse.")

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("⬅️ Dashboard"):
        st.switch_page("Dashboard.py")
with col2:
    if st.button("🏠 Accueil"):
        st.switch_page("Accueil.py")
