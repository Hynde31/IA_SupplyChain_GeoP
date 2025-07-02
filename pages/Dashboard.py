import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
from geo_zones import ZONES_GEO
from ai_models import geopolitical_risk_score
from mapping import mrp_colors, cities_coords, generate_legend

st.set_page_config(page_title="Dashboard IA Supply Chain", layout="wide")

@st.cache_data
def load_suppliers(path="mapping_fournisseurs.csv"):
    df = pd.read_csv(path)
    df = df.fillna("")
    return df

# Chargement des données
df_sup = load_suppliers()
if df_sup.empty:
    st.warning("Aucun fournisseur. Merci de vérifier le fichier.")
    st.stop()

if "mrp_codes" in st.session_state and st.session_state["mrp_codes"]:
    mrp_selected = [str(code).strip().upper() for code in st.session_state["mrp_codes"]]
else:
    st.error("Aucun portefeuille MRP sélectionné. Retournez à l'accueil.")
    st.stop()

df_sup["Portefeuille"] = df_sup["Portefeuille"].astype(str).str.strip().str.upper()
df_sup["Ville"] = df_sup["Ville"].astype(str).str.strip()

# Attribution coordonnées
df_sup["Latitude"] = df_sup["Ville"].map(lambda v: cities_coords.get(v, (np.nan, np.nan))[0])
df_sup["Longitude"] = df_sup["Ville"].map(lambda v: cities_coords.get(v, (np.nan, np.nan))[1])
df_sup["Coordonnée connue"] = (~df_sup["Latitude"].isna()) & (~df_sup["Longitude"].isna())

# Calcul des risques
df_sup["Score risque géopolitique"] = df_sup.apply(lambda r: geopolitical_risk_score(r, ZONES_GEO), axis=1)
df_sup["Score (%)"] = (df_sup["Score risque géopolitique"] * 100).round(1)
df_sup["Alerte"] = df_sup["Score risque géopolitique"].apply(
    lambda s: "🟥 Critique" if s >= 0.7 else ("🟧 Surveille" if s >= 0.5 else "🟩 OK")
)
df_sup["Couleur MRP"] = df_sup["Portefeuille"].apply(lambda x: mrp_colors.get(x, mrp_colors["DEFAULT"]))
df_sup["type"] = "Fournisseur"

# Zones géopolitiques
df_geo = pd.DataFrame(ZONES_GEO)
df_geo["Couleur MRP"] = df_geo["Couleur"]
df_geo["type"] = "Zone"

df_map = pd.concat([df_sup, df_geo], ignore_index=True)

# Vue cartographique
center_lat = df_sup["Latitude"].mean() if not df_sup["Latitude"].isna().all() else 46.7
center_lon = df_sup["Longitude"].mean() if not df_sup["Longitude"].isna().all() else 2.4

layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_map,
    get_position='[Longitude, Latitude]',
    get_color="Couleur MRP",
    get_radius=60000,
    pickable=True,
    auto_highlight=True,
)

tooltip = {
    "html": """
    <b>Type:</b> {type}<br>
    <b>MRP:</b> {Portefeuille}<br>
