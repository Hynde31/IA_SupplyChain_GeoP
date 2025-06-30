import streamlit as st
import pandas as pd
import pydeck as pdk
from datetime import datetime
import geo_news_nlp

st.set_page_config(page_title="Dashboard Supply Chain", layout="wide")

# 0. Sélection du portefeuille
mrp_codes = st.session_state.get("mrp_codes", [])
if not mrp_codes:
    st.warning("Vous devez d'abord définir votre portefeuille MRP sur la page Accueil.")
    st.stop()

# 1. Chargement des données fournisseurs (depuis le CSV)
@st.cache_data
def load_suppliers(path="mapping_fournisseurs.csv"):
    df = pd.read_csv(path)
    # Nettoyage basique
    df["MRP"] = df["Portefeuille"].str.upper().str.strip()
    df["Site prod"] = df["Site prod"].fillna("")  # Pour éviter les NaN
    return df

df_sup = load_suppliers()
df_sup = df_sup[df_sup["Portefeuille"].isin(mrp_codes)]

# 2. Extraction coordonnées (pour la map, à adapter selon réalités)
@st.cache_data
def geocode_city(city, country):
    # Mapping rapide, à remplacer par un vrai service si besoin
    coords = geo_news_nlp.QUICK_COORDS.get(city) or geo_news_nlp.QUICK_COORDS.get(country)
    return coords if coords else (None, None)

df_sup[["latitude", "longitude"]] = df_sup.apply(
    lambda row: pd.Series(geocode_city(row["Ville"], row["Pays"])),
    axis=1
)

# 3. Construction DataFrame pour la carte fournisseurs
df_fournisseurs_map = df_sup.dropna(subset=["latitude", "longitude"]).copy()
df_fournisseurs_map["type"] = "Fournisseur"
df_fournisseurs_map["label"] = df_fournisseurs_map["Fournisseur"]
df_fournisseurs_map["Couleur"] = [[0, 102, 204]] * len(df_fournisseurs_map)
df_fournisseurs_map["Impact"] = ""
df_fournisseurs_map["Criticité"] = "Élevée"  # À adapter selon tes règles

# 4. Zones géopolitiques à risque (issues du module d'analyse)
# Choix du mois courant pour la veille auto
today = datetime.today().strftime("%Y-%m")
news, geopolitics = geo_news_nlp.get_news_impact_for_month(today)
df_geo = pd.DataFrame(geopolitics)
if not df_geo.empty:
    df_geo["type"] = "Zone à risque"
    df_geo["label"] = df_geo["zone"]
    df_geo["MRP Code"] = ""
    df_geo["Désignation"] = ""
    df_geo["Pays"] = df_geo["zone"]
    df_geo["Site"] = ""
    df_geo["Couleur"] = df_geo["impact"].map({3: [220,30,30], 2: [255,140,0], 1: [255,215,0]})
    df_geo["Criticité"] = ""
    df_geo["Impact"] = "Détecté actu"
else:
    df_geo = pd.DataFrame(columns=df_fournisseurs_map.columns)

# 5. Fusion pour la carte
df_map = pd.concat([df_fournisseurs_map, df_geo[df_fournisseurs_map.columns]], ignore_index=True)

# 6. Affichage carte interactive
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
        <b>Pays:</b> {Pays}<br>
        <b>Site:</b> {Site}<br>
        <b>Impact:</b> {Impact}<br>
        <b>Criticité:</b> {Criticité}<br>
    """,
    "style": {"backgroundColor": "#262730", "color": "white"}
}

st.subheader("Carte des fournisseurs et zones géopolitiques à risque")
st.pydeck_chart(
    pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip
    )
)
st.caption(":blue[• Fournisseurs]  |  :red[• Zones à risque géopolitique]  |  :orange[• Zones conflit armé]  |  :yellow[• Zones tensions majeures]")

st.divider()

# 7. KPIs réalistes (calculés à partir des données)
nb_mrp = df_sup["Portefeuille"].nunique()
nb_fournisseurs = df_sup["Fournisseur"].nunique()
nb_pays = df_sup["Pays"].nunique()
nb_sites = df_sup["Site prod"].nunique()
nb_sites_risque = df_fournisseurs_map[df_fournisseurs_map["Criticité"] == "Élevée"].shape[0]
ruptures_cours = 0  # À remplacer par une vraie logique/colonne si dispo
dual_sourcing_pct = int((df_sup.groupby("Pièce")["Fournisseur"].nunique() > 1).mean() * 100)
score_risque_moyen = 2.4  # À calculer si tu as des scores réels
otd_moyen = 97  # À remplacer si tu as des vraies données OTD

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

# 8. Vision Approvisionneur (tableau)
st.header("Vision Approvisionneur : Statuts MRP / Fournisseurs")
df_sup["ALERTE"] = ""
# Détection auto : fournisseur dans un pays à risque géopolitique ?
risk_zones = set(df_geo["zone"]) if not df_geo.empty else set()
df_sup["ALERTE"] = df_sup["Pays"].apply(lambda p: "Zone à risque" if p in risk_zones else "")
st.dataframe(
    df_sup[
        ["Portefeuille", "Pièce", "Fournisseur", "Site prod", "Pays", "Ville", "ALERTE"]
    ],
    use_container_width=True,
    hide_index=True
)

st.divider()
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("🏠 Accueil"):
        st.switch_page("Accueil")
with col2:
    if st.button("Veille géopolitique ➡️"):
        st.switch_page("GeopoliticalNews")
