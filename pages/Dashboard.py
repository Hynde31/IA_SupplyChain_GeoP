import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
from geo_zones import ZONES_GEO
from ai_models import geopolitical_risk_score
from mapping import ID_colors, cities_coords, generate_legend

st.set_page_config(page_title="Dashboard IA Supply Chain", layout="wide")

@st.cache_data
def load_suppliers(path="mapping_fournisseurs.csv"):
    return pd.read_csv(path).fillna("")

df_sup = load_suppliers()
if df_sup.empty:
    st.warning("Aucun fournisseur. Merci de vérifier le fichier.")
    st.stop()

# 1. Récupérer le(s) portefeuille(s) sélectionné(s) depuis la session
ID_selected = st.session_state.get("ID_codes", [])
if not ID_selected:
    st.error("Aucun portefeuille ID sélectionné. Retournez à l'accueil pour choisir votre portefeuille.")
    st.stop()

# 2. Filtrer les données en fonction du/des portefeuille(s) choisis
col_portefeuille = [col for col in df_sup.columns if col.strip().lower() == "portefeuille"]
if col_portefeuille:
    col_portefeuille = col_portefeuille[0]
else:
    st.error("La colonne 'Portefeuille' est absente du CSV.")
    st.stop()

df_sup[col_portefeuille] = df_sup[col_portefeuille].astype(str).str.strip().str.upper()
df_sup = df_sup[df_sup[col_portefeuille].isin(ID_selected)].copy()

# 3. Géolocalisation fournisseurs
df_sup["Ville"] = df_sup["Ville"].astype(str).str.strip()
df_sup["Latitude"] = df_sup["Ville"].map(lambda v: cities_coords.get(v, (np.nan, np.nan))[0])
df_sup["Longitude"] = df_sup["Ville"].map(lambda v: cities_coords.get(v, (np.nan, np.nan))[1])

# 4. Score risque géopolitique
df_sup["Score risque géopolitique"] = df_sup.apply(lambda r: geopolitical_risk_score(r, ZONES_GEO), axis=1)
df_sup["Score (%)"] = (df_sup["Score risque géopolitique"] * 100).round(1)
df_sup["Score_pct"] = df_sup["Score (%)"]  # colonne sans espace pour tooltip
df_sup["Alerte"] = df_sup["Score risque géopolitique"].apply(
    lambda s: "🟥 Critique" if s >= 0.7 else ("🟧 Surveille" if s >= 0.5 else "🟩 OK")
)
df_sup["Portefeuille"] = df_sup[col_portefeuille]
df_sup["type"] = "Fournisseur"
df_sup["label"] = df_sup.get("Fournisseur", df_sup.get(col_portefeuille, ""))

# Helper: normalize color to RGBA list for pydeck
def ensure_rgba(col):
    if not isinstance(col, (list, tuple)):
        return [200, 200, 200, 255]
    col = list(col)
    if len(col) == 3:
        col.append(255)
    return [int(col[0]), int(col[1]), int(col[2]), int(col[3])]

#  --- Couleurs fournisseurs ---
# Use ID_colors mapping but make sure it's RGBA
color_dict = ID_colors if isinstance(ID_colors, dict) else {}
def get_supplier_color(id_code):
    # Force HEL to the blue used in mapping (or fallback)
    if str(id_code).upper() == "HEL":
        return ensure_rgba(color_dict.get("HEL", [57, 106, 177]))
    return ensure_rgba(color_dict.get(id_code, color_dict.get("DEFAULT", [200,200,200])))

df_sup["Couleur ID"] = df_sup[col_portefeuille].apply(get_supplier_color)

# 5. Préparation zones géopolitiques
df_geo = pd.DataFrame(ZONES_GEO).copy()
# Decide color for zones: red for 'zones de conflit' (impact >= 0.6), otherwise orange (zones à risque)
def zone_color_from_impact(row):
    try:
        impact = float(row.get("Impact", np.nan))
    except Exception:
        impact = np.nan
    if pd.notna(impact) and impact >= 0.6:
        return [255, 0, 0, 255]  # rouge pour conflit
    else:
        return [255, 165, 0, 255]  # orange pour risque
# If the zone already has a 'Couleur' key we still override based on impact to fit the requested scheme
df_geo["Couleur ID"] = df_geo.apply(zone_color_from_impact, axis=1)
df_geo["type"] = "Crise géopolitique"
df_geo["Fournisseur"] = ""
df_geo["Pays"] = df_geo["Nom"]
df_geo["label"] = df_geo["Nom"]
df_geo["Portefeuille"] = ""  # empty to avoid tooltip key errors

# 6. Fusion pour la map (utilisé for layer data combine)
df_map = pd.concat([df_sup, df_geo], ignore_index=True, sort=False)

# 7. Build coordinates column expected by pydeck: [lon, lat]
df_map["Latitude"] = pd.to_numeric(df_map.get("Latitude"), errors="coerce")
df_map["Longitude"] = pd.to_numeric(df_map.get("Longitude"), errors="coerce")
df_map["coordinates"] = df_map.apply(
    lambda r: [float(r["Longitude"]), float(r["Latitude"])] if pd.notna(r["Latitude"]) and pd.notna(r["Longitude"]) else None,
    axis=1
)

# Filter valid points for layers
df_map_valid = df_map[df_map["coordinates"].notna()].copy()

if df_map_valid.empty:
    st.warning("Aucun point géolocalisé à afficher. Vérifiez la correspondance Ville -> cities_coords.")
    st.stop()

# set center from suppliers if exist else from zones
suppliers_coords = df_sup.dropna(subset=["Latitude", "Longitude"])
if not suppliers_coords.empty:
    center_lat = float(suppliers_coords["Latitude"].mean())
    center_lon = float(suppliers_coords["Longitude"].mean())
else:
    # fallback to average of df_map_valid
    center_lat = float(df_map_valid["Latitude"].mean())
    center_lon = float(df_map_valid["Longitude"].mean())

# Prepare two separate datasets for layers so coloring logic is consistent
zones_layer_df = df_map_valid[df_map_valid["type"] == "Crise géopolitique"].copy()
suppliers_layer_df = df_map_valid[df_map_valid["type"] == "Fournisseur"].copy()

# Ensure color fields are lists of ints length 4
zones_layer_df["Couleur ID"] = zones_layer_df["Couleur ID"].apply(ensure_rgba)
suppliers_layer_df["Couleur ID"] = suppliers_layer_df["Couleur ID"].apply(ensure_rgba)

# Set radii (zones bigger)
suppliers_layer_df["radius"] = suppliers_layer_df.get("radius", 50000)
zones_layer_df["radius"] = zones_layer_df.get("radius", 200000)

# Layers
zones_layer = pdk.Layer(
    "ScatterplotLayer",
    data=zones_layer_df,
    get_position="coordinates",
    get_color="Couleur ID",
    get_radius="radius",
    radius_scale=1.2,
    radius_min_pixels=6,
    radius_max_pixels=400,
    pickable=True,
    auto_highlight=True,
)

suppliers_layer = pdk.Layer(
    "ScatterplotLayer",
    data=suppliers_layer_df,
    get_position="coordinates",
    get_color="Couleur ID",
    get_radius="radius",
    radius_scale=1.0,
    radius_min_pixels=3,
    radius_max_pixels=200,
    pickable=True,
    auto_highlight=True,
)

# Text layer: show labels for zones and suppliers (we keep small to avoid clutter)
text_df = pd.concat([
    zones_layer_df[["coordinates", "label", "Couleur ID"]],
    suppliers_layer_df[["coordinates", "label", "Couleur ID"]]
], ignore_index=True).rename(columns={"coordinates": "coordinates", "label": "label", "Couleur ID": "Couleur ID"})
# Ensure coordinates present in text_df
text_df = text_df.assign(Longitude=text_df["coordinates"].map(lambda c: c[0]), Latitude=text_df["coordinates"].map(lambda c: c[1]))
text_df["coordinates"] = text_df.apply(lambda r: [r["Longitude"], r["Latitude"]], axis=1)

text_layer = pdk.Layer(
    "TextLayer",
    data=text_df,
    get_position="coordinates",
    get_text="label",
    get_color="Couleur ID",
    get_size=12,
    get_alignment_baseline='"bottom"',
    pickable=False,
)

# Tooltip (use Score_pct column for suppliers)
tooltip = {
    "html": """
    <b>Type:</b> {type}<br>
    <b>ID:</b> {Portefeuille}<br>
    <b>Fournisseur:</b> {Fournisseur}<br>
    <b>Pays:</b> {Pays}<br>
    <b>Ville:</b> {Ville}<br>
    <b>Score risque:</b> {Score_pct} / 100<br>
    <b>Alerte:</b> {Alerte}<br>
    <b>Zone:</b> {Nom}<br>
    <b>Description:</b> {Description}<br>
    <b>Cas:</b> {Cas}
    """,
    "style": {"backgroundColor": "#262730", "color": "white"}
}

# Display map
st.markdown(
    f"## 🌍 Carte des fournisseurs et crises géopolitiques – Portefeuille{'s' if len(ID_selected)>1 else ''} {', '.join(ID_selected)}"
)
st.caption("Visualisez les localisations de vos fournisseurs critiques ainsi que les zones de crises géopolitiques majeures pouvant impacter la chaîne d'approvisionnement Airbus.")
deck = pdk.Deck(
    layers=[zones_layer, suppliers_layer, text_layer],
    initial_view_state=pdk.ViewState(longitude=center_lon, latitude=center_lat, zoom=2.1),
    tooltip=tooltip
)
st.pydeck_chart(deck)

# Custom legend to match the requested colors exactly
legend_html = """
**Légende (couleurs forcées) :**<br>
- <span style="color:rgb(57,106,177);font-size:18px;">&#9679;</span> Fournisseur portefeuille <b>HEL</b><br>
- <span style="color:rgb(255,165,0);font-size:18px;">&#9679;</span> <b>Zones à risque géopolitique</b><br>
- <span style="color:rgb(255,0,0);font-size:18px;">&#9679;</span> <b>Zones de conflit</b><br>
"""
# Show both computed legend and the forced-color legend for clarity
st.markdown(generate_legend(ID_selected), unsafe_allow_html=True)
st.markdown(legend_html, unsafe_allow_html=True)

# 7. KPIs pertinents pour la prévention des retards/manquants
st.markdown("---")
st.markdown("### 📊 Indicateurs de risque et prévention des retards/manquants")

def kpi_fmt(val, unit="", percent=False):
    if pd.isnull(val): return "-"
    if percent:
        return f"{val:.1f}%"
    elif isinstance(val, float):
        return f"{val:.1f} {unit}".strip()
    else:
        return f"{val} {unit}".strip()

kpi_cols = {
    "CA annuel (M€)": ("CA total fournisseurs (M€)", False),
    "Volume pièces/an": ("Volume total pièces/an", False),
    "Dépendance Airbus (%)": ("Dépendance moyenne Airbus", True),
    "Délai moyen (jours)": ("Délai moyen global (jours)", False),
    "Score (%)": ("Score moyen risque géopolitique", True),
}
cols = st.columns(len(kpi_cols))
for i, (csv_col, (label, is_percent)) in enumerate(kpi_cols.items()):
    if csv_col in df_sup.columns:
        if is_percent:
            val = df_sup[csv_col].mean()
            show_val = kpi_fmt(val, percent=True)
        elif "Score" in label:
            val = df_sup[csv_col].mean()
            show_val = kpi_fmt(val, unit="/100")
        else:
            val = df_sup[csv_col].sum()
            show_val = kpi_fmt(val)
        cols[i].metric(label, show_val)
    else:
        cols[i].error(f"Colonne absente : {csv_col}")

# 8. Dataframe détaillé
st.markdown("---")
st.markdown("### 📋 Détail des fournisseurs suivis")
st.dataframe(
    df_sup[
        [col_portefeuille, "Fournisseur", "Pays", "Ville", "Score (%)", "Alerte", "CA annuel (M€)", "Dépendance Airbus (%)", "Délai moyen (jours)", "Volume pièces/an"]
        if "CA annuel (M€)" in df_sup.columns else df_sup.columns
    ],
    use_container_width=True,
    hide_index=True
)
