import streamlit as st
import pandas as pd
import pydeck as pdk
from geo_zones import ZONES_GEO

st.set_page_config(page_title="Dashboard Supply Chain", layout="wide")

mrp_codes = st.session_state.get("mrp_codes", [])
if not mrp_codes:
    st.warning("Vous devez d'abord définir votre portefeuille MRP sur la page Accueil.")
    st.stop()

@st.cache_data
def load_suppliers(path="mapping_fournisseurs.csv"):
    df = pd.read_csv(path)
    df["MRP"] = df["Portefeuille"].str.upper().str.strip()
    df["Site prod"] = df["Site prod"].fillna("-")
    df["Pièce"] = df["Pièce"].fillna("-")
    df["Fournisseur"] = df["Fournisseur"].fillna("-")
    df["Pays"] = df["Pays"].fillna("-")
    df["Ville"] = df["Ville"].fillna("-")
    return df

df_sup = load_suppliers()
df_sup = df_sup[df_sup["Portefeuille"].isin(mrp_codes)]

# Géocodage fictif ou réel selon données disponibles
QUICK_COORDS = {
    "Paris": (48.8566, 2.3522), "Lyon": (45.75, 4.85), "Berlin": (52.52, 13.4050),
    "Shanghai": (31.2304, 121.4737), "Chicago": (41.8781, -87.6298), "Izmir": (38.4192, 27.1287),
    "France": (46.603354, 1.888334), "Allemagne": (51.1657, 10.4515), "Chine": (35.8617, 104.1954),
    "USA": (37.0902, -95.7129), "Turquie": (38.9637, 35.2433),
}

def geocode_city(city, country):
    coords = QUICK_COORDS.get(city) or QUICK_COORDS.get(country)
    return coords if coords else (None, None)

# Remplissage des coordonnées
if not df_sup.empty:
    coords = df_sup.apply(lambda row: pd.Series(geocode_city(row["Ville"], row["Pays"])), axis=1)
    coords.columns = ["latitude", "longitude"]
    df_sup = pd.concat([df_sup.reset_index(drop=True), coords], axis=1)
else:
    df_sup["latitude"] = []
    df_sup["longitude"] = []

# Fournisseurs pour carte
df_fournisseurs_map = df_sup.dropna(subset=["latitude", "longitude"]).copy()
df_fournisseurs_map["type"] = "Fournisseur"
df_fournisseurs_map["label"] = df_fournisseurs_map["Fournisseur"]
df_fournisseurs_map["Couleur"] = [[0, 102, 204]] * len(df_fournisseurs_map)
df_fournisseurs_map["Impact"] = "Approvisionnement"
df_fournisseurs_map["Criticité"] = "Élevée"

# Zones géopolitiques
df_geo = pd.DataFrame(ZONES_GEO)
df_geo = df_geo.reindex(columns=df_fournisseurs_map.columns, fill_value="-")

# Fusion pour carte
df_map = pd.concat([df_fournisseurs_map, df_geo], ignore_index=True)

# Carte pydeck
if not df_map.empty:
    center_lat, center_lon = df_map["latitude"].astype(float).mean(), df_map["longitude"].astype(float).mean()
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
st.caption(":blue[• Fournisseurs]  |  :orange[• Zones à risque géopolitique]  |  :red[• Zones conflit armé]  |  :yellow[• Zones tension majeure]")

st.divider()

# KPIs
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

# Tableau Approvisionneur, valeurs par défaut si manquantes
for col in ["Portefeuille", "Pièce", "Fournisseur", "Site prod", "Pays", "Ville"]:
    if col not in df_sup.columns:
        df_sup[col] = "-"
    df_sup[col] = df_sup[col].replace("", "-").fillna("-")

df_sup["ALERTE"] = "-"
risk_zones = set(df_geo["Pays"]) if not df_geo.empty else set()
df_sup["ALERTE"] = df_sup["Pays"].apply(lambda p: "Zone à risque" if p in risk_zones else "OK")

st.header("Vision Approvisionneur : Statuts MRP / Fournisseurs")
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
