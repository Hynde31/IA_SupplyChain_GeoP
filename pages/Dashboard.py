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

# Dictionnaire coordonnées villes/fournisseurs (à compléter au besoin)
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
    "DEFAULT": [200, 200, 200],
}

df_sup = load_suppliers()
if df_sup.empty:
    st.warning("Aucun fournisseur. Merci de vérifier le fichier.")
    st.stop()

# Lecture du portefeuille sélectionné sur la page d'accueil
if "mrp_codes" in st.session_state and st.session_state["mrp_codes"]:
    mrp_selected = [str(code).strip().upper() for code in st.session_state["mrp_codes"]]
else:
    st.error("Aucun portefeuille MRP sélectionné. Retournez à l'accueil.")
    st.stop()

df_sup["Portefeuille"] = df_sup["Portefeuille"].astype(str).str.strip().str.upper()
df_sup["Ville"] = df_sup["Ville"].astype(str).str.strip()

# Ajoute colonnes latitude/longitude pour chaque fournisseur (si connues)
df_sup["Latitude"] = df_sup["Ville"].map(lambda v: cities_coords.get(v, (None, None))[0])
df_sup["Longitude"] = df_sup["Ville"].map(lambda v: cities_coords.get(v, (None, None))[1])
df_sup["Coordonnée connue"] = df_sup["Ville"].map(lambda v: v in cities_coords)

df_sup["Score risque géopolitique"] = df_sup.apply(lambda r: geopolitical_risk_score(r, ZONES_GEO), axis=1)
df_sup["Score (%)"] = (df_sup["Score risque géopolitique"]*100).round(1)
df_sup["Alerte"] = df_sup["Score risque géopolitique"].apply(
    lambda s: "🟥 Critique" if s >= 0.7 else ("🟧 Surveille" if s >= 0.5 else "🟩 OK")
)
df_sup["Couleur MRP"] = df_sup["Portefeuille"].apply(
    lambda x: mrp_colors.get(x, mrp_colors["DEFAULT"])
)

# Filtrage strict par portefeuille MRP choisi ET uniquement les fournisseurs géolocalisables
df_sup_display = df_sup[
    (df_sup["Portefeuille"].isin(mrp_selected)) & (df_sup["Coordonnée connue"])
].copy()

df_sup_display["type"] = "Fournisseur"

# Ajout zones géopolitiques (affichées en orange/rouge)
df_geo = pd.DataFrame(ZONES_GEO)
df_geo["Couleur MRP"] = df_geo["Couleur"]
df_geo["type"] = df_geo["type"]

df_map = pd.concat([df_sup_display, df_geo], ignore_index=True)

# Calcul du centre de la carte (sécurisé)
if not df_sup_display.empty:
    center_lat = pd.to_numeric(df_sup_display["Latitude"], errors="coerce").mean()
    center_lon = pd.to_numeric(df_sup_display["Longitude"], errors="coerce").mean()
else:
    # fallback : centre France/Europe
    center_lat, center_lon = 46.7, 2.4

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

st.subheader(f"🌍 Carte des fournisseurs du portefeuille {', '.join(mrp_selected)} et des zones à risque")

if df_sup_display.empty:
    st.warning("Aucun fournisseur localisable pour ce portefeuille (ville inconnue ou portefeuille vide).")
    villes_absentes = df_sup[
        (df_sup["Portefeuille"].isin(mrp_selected)) & (~df_sup["Coordonnée connue"])
    ][["Fournisseur", "Ville", "Portefeuille"]]
    if not villes_absentes.empty:
        st.info("Villes absentes du dictionnaire de coordonnées :")
        st.dataframe(villes_absentes, use_container_width=True, hide_index=True)
else:
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip))

    # Légende dynamique : uniquement les portefeuilles sélectionnés + zones géopolitiques/conflit
    legend_lines = ["**Légende carte :**"]
    color_hex = lambda rgb: f"rgb({rgb[0]},{rgb[1]},{rgb[2]})"
    for mrp in mrp_selected:
        col = color_hex(mrp_colors.get(mrp, mrp_colors["DEFAULT"]))
        legend_lines.append(
            f'- <span style="color:{col};font-size:22px;">&#9679;</span> Fournisseur portefeuille <b>{mrp}</b>'
        )
    legend_lines.append('- <span style="color:orange;font-size:22px;">&#9679;</span> <b>Zones à risque géopolitique</b>')
    legend_lines
