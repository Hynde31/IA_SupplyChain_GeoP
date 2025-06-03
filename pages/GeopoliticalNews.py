import streamlit as st

st.set_page_config(page_title="Veille géopolitique Supply Chain", layout="wide")

from geo_news_nlp import get_news_impact_for_month
import pandas as pd

st.title("Veille géopolitique Supply Chain")
st.write(
    """
    Ce tableau de bord analyse les actualités géopolitiques pouvant impacter la supply chain.
    Entrez un mois pour lancer la veille automatique.
    """
)

month = st.text_input("Mois à surveiller (format AAAA-MM)", "2025-05")

if st.button("Analyser ce mois"):
    news, impacts = get_news_impact_for_month(month)

    if news is not None and len(news) > 0:
        st.subheader("Actualités du mois sélectionné")
        for entry in news:
            st.markdown(f"**{entry['date']}** — {entry['title']}")
            if entry.get("summary"):
                st.caption(entry['summary'])
    else:
        st.info("Aucune actualité trouvée pour ce mois.")

    # --- Affichage de la carte interactive ---
    if impacts is not None and len(impacts) > 0:
        st.subheader("Carte des zones géographiques à risque détectées")
        df = pd.DataFrame(impacts)
        df = df.rename(columns={"lat": "latitude", "lon": "longitude"})
        st.map(df)

        st.subheader("Zones à risque détectées")
        for imp in impacts:
            st.write(
                f"- {imp['zone']} (lat: {imp['latitude']}, lon: {imp['longitude']}) — Score d’impact : {imp['impact']}"
            )
    elif impacts == [] and news is not None:
        st.info("Aucun impact géopolitique détecté pour ce mois.")
    elif impacts is None:
        st.warning("Analyse NLP non disponible dans cet environnement.")
else:
    st.info("Entrez un mois et cliquez sur Analyser pour lancer la veille.")
