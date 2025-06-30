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

# Dictionnaire coordonnées villes/fournisseurs
cities_coords = {
    "Kyriat Gat": (31.6097, 34.7604),
    "Rousset": (43.4285, 5.5872),
    "Shizuoka": (34.9756, 138.3828),
    "Bensheim": (49.6803, 8.6195),
    "Haïfa": (32.7940, 34.9896),
    "Angers": (47.4784, -0.5632),
    "Shanghai": (31.2304, 121.4737),
    "Beersheba": (31.2518, 34.7913),
    "Kyoto": (35.0116, 135.7681)
}

# Couleurs par portefeuille MRP
mrp_colors = {
    "HEL": [57, 106, 177],
    "EBE": [218, 124, 48],
    "DWI": [62, 150, 81],
    # Couleur par défaut
    "DEFAULT": [200, 200, 200],
}

df_sup = load_suppliers()
if df_sup.empty:
    st.warning("Aucun fournisseur. Merci de vérifier le fichier.")
    st.stop()

# Lecture du portefeuille sélectionné sur la page d'accueil
mrp_selected = []
if "mrp_codes" in st.session_state and st.session_state["mrp_codes"]:
    mrp_selected = [str(code).strip().upper() for code in st.session_state["mrp_codes"]]
else:
    st.error("Aucun portefeuille MRP sélectionné. Retournez à l'accueil.")
    st.stop()

# Ajoute colonnes latitude/longitude pour chaque fournisseur (si connues)
df_sup["Latitude"] = df_sup["Ville"].map(lambda v: cities_coords.get(v, (None, None))[0])
df_sup["Longitude"] = df_sup["Ville"].map(lambda v: cities_coords.get(v, (None, None))[1])

df_sup["Score risque géopolitique"] = df_sup.apply(lambda r: geopolitical_risk_score(r, ZONES_GEO), axis=1)
df_sup["Score (%)"] = (df_sup["Score risque géopolitique"]*100).round(1)
df_sup["Alerte"] = df_sup["Score risque géopolitique"].apply(
    lambda s: "🟥 Critique" if s >= 0.7 else ("🟧 Surveille" if s >= 0.5 else "🟩 OK")
)
df_sup["Couleur MRP"] = df_sup["Portefeuille"].apply(lambda x: mrp_colors.get(str(x).strip().upper(), mrp_colors["DEFAULT"]))

# Filtrage par portefeuille MRP choisi
df_sup_display = df_sup[
    df_sup["Portefeuille"].str.strip().str.upper().isin(mrp_selected)
].dropna(subset=["Latitude", "Longitude"])
df_sup_display["type"] = "Fournisseur"

# Ajout zones géopolitiques
df_geo = pd.DataFrame(ZONES_GEO)
df_geo["Couleur MRP"] = df_geo["Couleur"]
df_geo["type"] = df_geo["type"]

df_map = pd.concat([df_sup_display, df_geo], ignore_index=True)

# Sécurisation de la conversion en float
center_lat = pd.to_numeric(df_map["Latitude"], errors="coerce").mean()
center_lon = pd.to_numeric(df_map["Longitude"], errors="coerce").mean()
if pd.isna(center_lat) or pd.isna(center_lon):
    center_lat, center_lon = 0, 0  # fallback

layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_map,
    get_position='[Longitude, Latitude]',
    get_color="Couleur MRP",
    get_radius=60000,
    pickable=True,
    auto_highlight=True,
)
view_state = pdk.ViewState(longitude=center_lon, latitude=center_lat, zoom=2.1, pitch=0)
tooltip = {
    "html": """
    <b>Type:</b> {type}<br>
    <b>MRP:</b> {Portefeuille}<br>
    <b>Fournisseur:</b> {Fournisseur}<br>
    <b>Pays:</b> {Pays}<br>
    <b>Ville:</b> {Ville}<br>
    <b>Score risque:</b> {Score (%)}/100<br>
    <b>Alerte:</b> {Alerte}
    """,
    "style": {"backgroundColor": "#262730", "color": "white"}
}

# Affichage
st.subheader(f"🌍 Carte des fournisseurs du portefeuille {', '.join(mrp_selected)} et des zones à risque")
st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip))

# Légende claire
st.markdown("""
**Légende carte :**
- <span style="color:rgb(57,106,177);font-weight:bold">●</span> Portefeuille HEL
- <span style="color:rgb(218,124,48);font-weight:bold">●</span> Portefeuille EBE
- <span style="color:rgb(62,150,81);font-weight:bold">●</span> Portefeuille DWI
- <span style="color:orange;font-weight:bold">●</span> Zones à risque géopolitique
- <span style="color:red;font-weight:bold">●</span> Zones de conflit
""", unsafe_allow_html=True)

st.divider()
st.subheader(f"📊 Fournisseurs du portefeuille {', '.join(mrp_selected)}")

st.dataframe(
    df_sup_display[
        ["Portefeuille", "Fournisseur", "Pays", "Ville", "Latitude", "Longitude", "Score (%)", "Alerte"]
    ],
    use_container_width=True,
    hide_index=True
)
