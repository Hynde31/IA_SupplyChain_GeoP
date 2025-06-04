import streamlit as st
import pandas as pd
import pydeck as pdk
from suppliers_data import SUPPLIERS
from utils import risk_gauge, kpi_card

st.set_page_config(page_title="Dashboard Supply Chain", layout="wide")

# 0. Sélection du portefeuille
mrp_codes = st.session_state.get("mrp_codes", [])
if not mrp_codes:
    st.warning("Vous devez d'abord définir votre portefeuille MRP sur la page Accueil.")
    st.stop()

# 1. Construction du DataFrame principal fournisseurs
def flatten_suppliers(suppliers, mrp_codes):
    rows = []
    for s in suppliers:
        if s["mrp_code"] not in mrp_codes:
            continue
        for site in s["sites"]:
            rows.append({
                "type": "Fournisseur",
                "label": s["name"],
                "MRP Code": s["mrp_code"],
                "Désignation": s["component"],
                "latitude": site["lat"],
                "longitude": site["lon"],
                "Criticité": s["criticality"],
                "Pays": site["country"],
                "Site": site["city"],
                "Couleur": [0, 102, 204],  # Bleu fournisseurs
                "Impact": "",
            })
    return pd.DataFrame(rows)

df_fournisseurs = flatten_suppliers(SUPPLIERS, mrp_codes)

# 2. Zones géopolitiques à risque (exemples, adapte selon tes besoins)
zones_geopol = pd.DataFrame([
    {
        "type": "Zone à risque",
        "label": "Mer Rouge",
        "MRP Code": "",
        "Désignation": "",
        "latitude": 16.3,
        "longitude": 42.6,
        "Criticité": "",
        "Pays": "Mer Rouge",
        "Site": "",
        "Couleur": [220, 30, 30],  # Rouge
        "Impact": "Blocage maritime",
    },
    {
        "type": "Zone à risque",
        "label": "Ukraine",
        "MRP Code": "",
        "Désignation": "",
        "latitude": 48.4,
        "longitude": 31.2,
        "Criticité": "",
        "Pays": "Ukraine",
        "Site": "",
        "Couleur": [255, 140, 0],  # Orange
        "Impact": "Conflit armé",
    },
    {
        "type": "Zone à risque",
        "label": "Taïwan",
        "MRP Code": "",
        "Désignation": "",
        "latitude": 23.7,
        "longitude": 121.0,
        "Criticité": "",
        "Pays": "Taïwan",
        "Site": "",
        "Couleur": [255, 215, 0],  # Jaune
        "Impact": "Tensions Chine/USA",
    },
])

# 3. Fusion des deux couches pour la carte
df_map = pd.concat([df_fournisseurs, zones_geopol], ignore_index=True)

# 4. Affichage pydeck
if not df_map.empty:
    center_lat, center_lon = df_map["latitude"].mean(), df_map["longitude"].mean()
else:
    center_lat, center_lon = 0, 0

layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_map,
    get_position='[longitude, latitude]',
    get_color="Couleur",
    get_radius=35000,
    pickable=True,
    auto_highlight=True,
)

view_state = pdk.ViewState(
    longitude=center_lon,
    latitude=center_lat,
    zoom=2.2,
    pitch=0,
)

tooltip = {
    "html": """
        <b>Type:</b> {type}<br>
        <b>Nom:</b> {label}<br>
        {% if Impact %}<b>Impact:</b> {Impact}<br>{% endif %}
        {% if Pays %}<b>Pays:</b> {Pays}<br>{% endif %}
        {% if Site %}<b>Site:</b> {Site}<br>{% endif %}
        {% if Criticité %}<b>Criticité:</b> {Criticité}<br>{% endif %}
    """,
    "style": {"backgroundColor": "#262730", "color": "white"}
}

st.subheader("Carte des fournisseurs et des zones géopolitiques à risque")
st.pydeck_chart(
    pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip
    )
)
st.caption(":blue[• Fournisseurs]  |  :red[• Zones à risque géopolitique]  |  :orange[• Zones conflit armé]  |  :yellow[• Zones tensions majeures]")

st.divider()

# 5. Calculs KPI (inchangé)
nb_mrp = df_fournisseurs["MRP Code"].nunique()
nb_fournisseurs = df_fournisseurs["label"].nunique()
nb_pays = df_fournisseurs["Pays"].nunique()
# Remplace par tes calculs KPI réels si besoin
nb_sites_risque = 0
otd_moyen = 0
score_risque_moyen = 0
ruptures_cours = 0
dual_sourcing_pct = 0

st.title("KPI Portefeuille - Supply Chain")
kpi1, kpi2, kpi3, kpi4, kpi5, kpi6, kpi7, kpi8 = st.columns(8)
kpi1.metric("MRP codes suivis", nb_mrp)
kpi2.metric("Fournisseurs actifs", nb_fournisseurs)
kpi3.metric("Sites à risque élevé", nb_sites_risque)
kpi4.metric("On-Time Delivery", f"{otd_moyen}%")
kpi5.metric("Ruptures en cours", ruptures_cours)
kpi6.metric("Score risque moyen", f"{score_risque_moyen:.2f}")
kpi7.metric("Dual sourcing", f"{dual_sourcing_pct}%")
kpi8.metric("Pays couverts", nb_pays)

st.divider()

# 6. Vision Approvisionneur (tableau)
st.header("Vision Approvisionneur : Statuts MRP / Fournisseurs")
if not df_fournisseurs.empty:
    df_fournisseurs["ALERTE"] = ""
    # Ajoute ici tes règles d'alerte selon les colonnes de df_fournisseurs
    st.dataframe(
        df_fournisseurs[
            ["MRP Code", "Désignation", "label", "Site", "Pays", "Criticité", "ALERTE"]
        ],
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Aucun fournisseur trouvé pour les codes MRP sélectionnés.")

st.divider()
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("🏠 Accueil"):
        st.switch_page("Accueil.py")
with col2:
    if st.button("Veille géopolitique ➡️"):
        st.switch_page("GeopoliticalNews.py")
