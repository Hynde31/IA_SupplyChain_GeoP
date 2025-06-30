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

# Carte : coordonnées pour villes/pays principaux
cities_coords = {
    "Meudon": (48.8131, 2.2350), "Valence": (44.9334, 4.8924), "Toulouse": (43.6047, 1.4442), "Olathe": (38.8814, -94.8191),
    "Phoenix": (33.4484, -112.0740), "Haïfa": (32.7940, 34.9896), "Schwäbisch Hall": (49.1203, 9.7376),
    "Tokyo": (35.6762, 139.6503), "Plaisir": (48.8275, 1.9533), "Nuremberg": (49.4521, 11.0767), "Rochefort": (45.9428, -0.9514),
    "Lake Forest": (33.6469, -117.6892), "Villaroche": (48.6013, 2.6637), "Derby": (52.9225, -1.4746),
    "Munich": (48.1351, 11.5820), "Cincinnati": (39.1031, -84.5120), "Middletown": (41.5623, -72.6506), "Hingham": (42.2418, -70.8898)
}
coords = df_sup.apply(lambda r: pd.Series(cities_coords.get(r["Ville"], (None, None))), axis=1)
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

st.subheader("🌍 Carte interactive des fournisseurs & zones à risque")
st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip))
st.caption(":green[• Risque faible]  |  :yellow[• Risque moyen]  |  :red[• Risque critique]  |  :orange[• Zones géopolitiques]")

st.divider()
st.subheader("📊 Tableau de suivi et alertes IA")
st.dataframe(
    df_sup[["Portefeuille", "Fournisseur", "Pays", "Ville", "Score (%)", "Alerte"]],
    use_container_width=True, hide_index=True
)
