import streamlit as st
import pandas as pd
from geo_news_nlp import get_news_impact_for_month

st.set_page_config(page_title="Veille géopolitique Supply Chain", layout="wide")

st.title("Veille géopolitique Supply Chain")
st.write(
    """
    Ce tableau de bord analyse les actualités géopolitiques pouvant impacter la supply chain.
    Sélectionnez un portefeuille pour afficher uniquement les alertes qui concernent vos sites fournisseurs.
    """
)

@st.cache_data
def load_mapping():
    return pd.read_csv("mapping_fournisseurs.csv")

# Charger le mapping
mapping = load_mapping()

# Sélection du portefeuille
portefeuilles = mapping["Portefeuille"].unique()
portefeuille_sel = st.selectbox("Choisissez un portefeuille", portefeuilles)

# Filtrer le mapping selon le portefeuille sélectionné
sites_portefeuille = mapping[mapping["Portefeuille"] == portefeuille_sel]

# Affichage du mapping filtré
st.subheader("Fournisseurs et sites couverts par ce portefeuille")
if not sites_portefeuille.empty:
    st.dataframe(
        sites_portefeuille[["Fournisseur", "Site prod", "Pays", "Ville"]].reset_index(drop=True)
    )
else:
    st.info("Aucun fournisseur ou site référencé pour ce portefeuille.")

# Création de la liste des pays et villes des sites à surveiller
pays_sites = set(sites_portefeuille["Pays"].str.lower()) | set(sites_portefeuille["Ville"].str.lower())

month = st.text_input("Mois à surveiller (format AAAA-MM)", "2025-05")

if st.button("Analyser ce mois"):
    news, impacts = get_news_impact_for_month(month)

    def lieux_news(news_item):
        """
        Retourne la liste des lieux détectés dans les champs 'places', 'title' et 'summary' d'une news.
        """
        fields = []
        if "places" in news_item and news_item["places"]:
            fields = [x.lower() for x in news_item["places"]]
        if "title" in news_item and news_item["title"]:
            fields += [news_item["title"].lower()]
        if "summary" in news_item and news_item["summary"]:
            fields += [news_item["summary"].lower()]
        return fields

    # Filtrer les news pertinentes pour le portefeuille sélectionné
    news_pertinentes = []
    for n in news if news else []:
        if any(any(site in champ for site in pays_sites) for champ in lieux_news(n)):
            news_pertinentes.append(n)

    if news_pertinentes:
        st.subheader("Actualités pertinentes pour votre portefeuille")
        for entry in news_pertinentes:
            st.markdown(f"**{entry['date']}** — {entry['title']}")
            if entry.get("summary"):
                st.caption(entry['summary'])
    else:
        st.info("Aucune actualité pertinente détectée pour votre portefeuille et ce mois.")

    # Carte interactive des impacts
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
    st.info("Sélectionnez un portefeuille, entrez un mois et cliquez sur Analyser.")

st.markdown("""
---
**Astuce :**  
Dans le mapping, le portefeuille "COE MRP EBE" comporte le fournisseur Intel, dont un site de production réel est à Kyriat Gat (Israël).
Si une actualité concerne Israël ou Kyriat Gat, elle remontera pour ce portefeuille.
""")
