import streamlit as st
import pandas as pd
import pydeck as pdk
from geo_zones import ZONES_GEO
from ai_models import geopolitical_risk_score

st.set_page_config(page_title="Dashboard IA Supply Chain", layout="wide")

@st.cache_data
def load_suppliers(path="mapping_fournisseurs.csv"):
    df = pd.read_csv(path)
    df = df.fillna("")
    return df

df_sup = load_suppliers()
if df_sup.empty:
    st.warning("Aucun fournisseur. Merci de vérifier le fichier.")
    st.stop()

# Scoring IA
df_sup["Score risque géopolitique"] = df_sup.apply(lambda r: geopolitical_risk_score(r, ZONES_GEO), axis=1)
df_sup["Score (%)"] = (df_sup["Score risque géopolitique"]*100).round(1)
df_sup["Alerte"] = df_sup["Score risque géopolitique"].apply(lambda s: "🟥 Critique" if s >= 0.7 else ("🟧 Surveille" if s >= 0.5 else "🟩 OK"))

# Carte
cities_coords = {
    "Toulouse": (43.6047, 1.4442), "Hambourg": (53.5511, 9.9937), "Tianjin": (39.3434, 117.3616),
    "France": (46.6, 1.88), "Allemagne": (51.1657, 10.4515), "Chine": (35.8617, 104.1954)
}
coords = df_sup.apply(lambda r: pd.Series(cities_coords.get(r["Ville"], cities_coords.get(r["Pays"], (None, None)))), axis=1)
coords.columns = ["latitude", "longitude"]
df_sup = pd.concat([df_sup, coords], axis=1)

df_sup_display = df_sup.dropna(subset=["latitude", "longitude"])
df_sup_display["Couleur"] = df_sup_display["Score risque géopolitique"].apply(
    lambda s: [220,30,30] if s>=0.7 else ([255,215,0] if s>=0.5 else [0,180,80])
)
df_sup_display["type"] = "Fournisseur"

# Ajout zones géo
df_geo = pd.DataFrame(ZONES_GEO)
df_geo = df_geo.reindex(columns=df_sup_display.columns, fill_value="-")
df_map = pd.concat([df_sup_display, df_geo], ignore_index=True)

layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_map,
    get_position='[longitude, latitude]',
    get_color="Couleur",
    get_radius=50000,
    pickable=True,
    auto_highlight=True,
)
center_lat, center_lon = df_map["latitude"].astype(float).mean(), df_map["longitude"].astype(float).mean()
view_state = pdk.ViewState(longitude=center_lon, latitude=center_lat, zoom=2.1, pitch=0)
tooltip = {"html": "<b>Type:</b> {type}<br><b>Nom:</b> {Fournisseur}<br><b>Pays:</b> {Pays}<br><b>Score risque:</b> {Score (%)}/100<br><b>Alerte:</b> {Alerte}", "style": {"backgroundColor": "#262730", "color": "white"}}

st.subheader("Carte interactive des fournisseurs et zones")
st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip))
st.caption(":green[• Risque faible]  |  :yellow[• Risque moyen]  |  :red[• Risque critique]  |  :orange[• Zones géopolitiques]")

st.divider()
st.subheader("Tableau de suivi et alertes IA")
st.dataframe(
    df_sup[["Portefeuille", "Fournisseur", "Pays", "Ville", "Score (%)", "Alerte"]],
    use_container_width=True, hide_index=True
)
