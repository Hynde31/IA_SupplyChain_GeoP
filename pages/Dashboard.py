import streamlit as st
import pandas as pd
import pydeck as pdk
from geo_zones import ZONES_GEO

st.set_page_config(page_title="Dashboard Supply Chain", layout="wide")

# Récupération du portefeuille MRP depuis la session
mrp_codes = st.session_state.get("mrp_codes", [])
if not mrp_codes:
    st.warning("Vous devez d'abord définir votre portefeuille MRP sur la page Accueil.")
    st.stop()

# Chargement des fournisseurs
@st.cache_data
def load_suppliers(path="mapping_fournisseurs.csv"):
    df = pd.read_csv(path)
    # Harmonisation
    df["MRP"] = df["Portefeuille"].str.upper().str.strip()
    df["Site prod"] = df["Site prod"].fillna("")
    return df

df_sup = load_suppliers()
df_sup = df_sup[df_sup["Portefeuille"].isin(mrp_codes)]

# Géocodage rapide des villes connues
QUICK_COORDS = {
    "Paris": (48.8566, 2.3522),
    "Lyon": (45.75, 4.85),
    "Toulouse": (43.6047, 1.4442),
    "Marseille": (43.3, 5.4),
    "Nantes": (47.2186, -1.5536),
    "Lille": (50.6333, 3.0667),
    "France": (46.603354, 1.888334),
    "Allemagne": (51.1657, 10.4515),
    "Germany": (51.1657, 10.4515),
    "Chine": (35.8617, 104.1954),
    "China": (35.8617, 104.1954),
    "USA": (37.0902, -95.7129),
    "États-Unis": (37.0902, -95.7129),
    "Espagne": (40.4637, -3.7492),
    "Italie": (41.8719, 12.5674),
    "Turkey": (38.9637, 35.2433),
    "Turquie": (38.9637, 35.2433),
    "Pologne": (51.9194, 19.1451),
    "Royaume-Uni": (55.3781, -3.4360),
    "Belgique": (50.5039, 4.4699),
    "Hongrie": (47.1625, 19.5033),
    "Maroc": (31.7917, -7.0926),
    "Tunisie": (33.8869, 9.5375),
    "Inde": (20.5937, 78.9629),
    "India": (20.5937, 78.9629),
    # Ajoute les villes/pays utiles à ton portefeuille
}

def geocode_city(city, country):
    coords = QUICK_COORDS.get(city) or QUICK_COORDS.get(country)
    return coords if coords else (None, None)

# Ajout latitude/longitude fournisseurs
if not df_sup.empty:
    coords = df_sup.apply(lambda row: pd.Series(geocode_city(row["Ville"], row["Pays"])), axis=1)
    coords.columns = ["latitude", "longitude"]
    df_sup = pd.concat([df_sup.reset_index(drop=True), coords], axis=1)
else:
    df_sup["latitude"] = []
    df_sup["longitude"] = []

df_fournisseurs_map = df_sup.dropna(subset=["latitude", "longitude"]).copy()
df_fournisseurs_map["type"] = "Fournisseur"
df_fournisseurs_map["label"] = df_fournisseurs_map["Fournisseur"]
df_fournisseurs_map["Couleur"] = [[0, 102, 204]] * len(df_fournisseurs_map)
df_fournisseurs_map["Impact"] = ""
df_fournisseurs_map["Criticité"] = "Élevée"

# Préparation des zones géopolitiques manuelles
df_geo = pd.DataFrame(ZONES_GEO)
if df_geo.empty:
    df_geo = pd.DataFrame(columns=df_fournisseurs_map.columns)
else:
    df_geo = df_geo.reindex(columns=df_fournisseurs_map.columns)

# Fusion pour la carte
df_map = pd.concat([df_fournisseurs_map, df_geo], ignore_index=True)

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

# KPIs dynamiques
nb_mrp = df_sup["Portefeuille"].nunique()
nb_fournisseurs = df_sup["Fournisseur"].nunique()
nb_pays = df_sup["Pays"].nunique()
nb_sites = df_sup["Site prod"].nunique()
nb_sites_risque = df_fournisseurs_map[df_fournisseurs_map["Criticité"] == "Élevée"].shape[0]
ruptures_cours = 0
dual_sourcing_pct = int((df_sup.groupby("Pièce")["Fournisseur"].nunique() > 1).mean() * 100) if not df_sup.empty else 0
score_risque_moyen = 2.4
otd_moyen = 97

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

# Tableau Approvisionneur
st.header("Vision Approvisionneur : Statuts MRP / Fournisseurs")
df_sup["ALERTE"] = ""
risk_zones = set(df_geo["label"]) if not df_geo.empty else set()
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
