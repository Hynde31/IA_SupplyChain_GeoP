import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
import traceback

# Imports protégés pour faciliter le debug si un module manque
try:
    from geo_zones import ZONES_GEO
except Exception:
    st.error("Erreur lors de l'import de geo_zones. Détails :")
    st.text(traceback.format_exc())
    st.stop()

try:
    from ai_models import geopolitical_risk_score
except Exception:
    st.error("Erreur lors de l'import de ai_models. Détails :")
    st.text(traceback.format_exc())
    st.stop()

# mapping.py expose ID_colors (vous avez précisé que vous gardez ce nom)
try:
    from mapping import ID_colors, cities_coords, generate_legend
except Exception:
    st.error("Erreur lors de l'import du module mapping. Détails :")
    st.text(traceback.format_exc())
    st.stop()

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
df_sup = df_sup[df_sup[col_portefeuille].isin(ID_selected)]

# 3. Géolocalisation fournisseurs (mapping cities_coords doit renvoyer (lat, lon))
df_sup["Ville"] = df_sup["Ville"].astype(str).str.strip()
df_sup["Latitude"] = df_sup["Ville"].map(lambda v: cities_coords.get(v, (np.nan, np.nan))[0])
df_sup["Longitude"] = df_sup["Ville"].map(lambda v: cities_coords.get(v, (np.nan, np.nan))[1])

# 4. Score risque géopolitique
df_sup["Score risque géopolitique"] = df_sup.apply(lambda r: geopolitical_risk_score(r, ZONES_GEO), axis=1)
df_sup["Score (%)"] = (df_sup["Score risque géopolitique"] * 100).round(1)
df_sup["Alerte"] = df_sup["Score risque géopolitique"].apply(
    lambda s: "🟥 Critique" if s >= 0.7 else ("🟧 Surveille" if s >= 0.5 else "🟩 OK")
)

#  --- Couleurs : utiliser le dict ID_colors fourni dans mapping.py ---
def ensure_rgba(col):
    if not isinstance(col, (list, tuple)):
        return [200, 200, 200, 255]
    col = list(col)
    if len(col) == 3:
        col.append(255)
    if len(col) >= 4:
        return col[:4]
    return [200, 200, 200, 255]

# Utiliser directement ID_colors (vous l'avez conservé sous ce nom)
color_dict = ID_colors if isinstance(ID_colors, dict) else {}

df_sup["Couleur ID"] = df_sup[col_portefeuille].apply(
    lambda x: ensure_rgba(color_dict.get(x, color_dict.get("DEFAULT", [200,200,200])))
)
df_sup["type"] = "Fournisseur"
df_sup["label"] = df_sup.get("Fournisseur", df_sup.get(col_portefeuille, ""))

# 5. Préparation zones géopolitiques
df_geo = pd.DataFrame(ZONES_GEO).copy()
df_geo["Latitude"] = pd.to_numeric(df_geo["Latitude"], errors="coerce")
df_geo["Longitude"] = pd.to_numeric(df_geo["Longitude"], errors="coerce")
df_geo["Couleur ID"] = df_geo["Couleur"].apply(ensure_rgba)
df_geo["type"] = "Crise géopolitique"
df_geo["Fournisseur"] = ""
df_geo["Pays"] = df_geo["Nom"]
df_geo["label"] = df_geo["Nom"]

# 6. Fusion pour la map (mais on gardera deux dataframes pour layers)
df_map = pd.concat([df_sup, df_geo], ignore_index=True, sort=False)

# Calcul du centre de la carte
valid_sup = df_sup.dropna(subset=["Latitude", "Longitude"])
center_lat = valid_sup["Latitude"].mean() if not valid_sup.empty else df_geo["Latitude"].mean()
center_lon = valid_sup["Longitude"].mean() if not valid_sup.empty else df_geo["Longitude"].mean()
if np.isnan(center_lat) or np.isnan(center_lon):
    center_lat, center_lon = 46.7, 2.4  # fallback

# 6a. Préparer layers séparés pour plus de contrôle
suppliers_layer_df = df_sup.dropna(subset=["Latitude", "Longitude"]).copy()
zones_layer_df = df_geo.dropna(subset=["Latitude", "Longitude"]).copy()

suppliers_layer_df["radius"] = 30000
if "Impact" in zones_layer_df.columns:
    zones_layer_df["radius"] = zones_layer_df["Impact"].apply(lambda x: max(80000, float(x) * 300000))
else:
    zones_layer_df["radius"] = 200000

zones_layer = pdk.Layer(
    "ScatterplotLayer",
    data=zones_layer_df,
    get_position='[Longitude, Latitude]',
    get_color="Couleur ID",
    get_radius="radius",
    radius_scale=1,
    radius_min_pixels=4,
    radius_max_pixels=200,
    pickable=True,
    auto_highlight=True,
)

suppliers_layer = pdk.Layer(
    "ScatterplotLayer",
    data=suppliers_layer_df,
    get_position='[Longitude, Latitude]',
    get_color="Couleur ID",
    get_radius="radius",
    radius_scale=1,
    radius_min_pixels=2,
    radius_max_pixels=100,
    pickable=True,
    auto_highlight=True,
)

text_df = pd.concat([
    suppliers_layer_df[["Longitude", "Latitude", "label", "Couleur ID"]],
    zones_layer_df[["Longitude", "Latitude", "label", "Couleur ID"]]
], ignore_index=True)

text_layer = pdk.Layer(
    "TextLayer",
    data=text_df,
    get_position='[Longitude, Latitude]',
    get_text="label",
    get_color="Couleur ID",
    get_size=14,
    get_alignment_baseline='"bottom"',
    pickable=False,
)

tooltip = {
    "html": """
    <b>Type:</b> {type}<br>
    <b>ID:</b> {Portefeuille}<br>
    <b>Fournisseur:</b> {Fournisseur}<br>
    <b>Pays:</b> {Pays}<br>
    <b>Ville:</b> {Ville}<br>
    <b>Score risque:</b> {Score (%)} / 100<br>
    <b>Alerte:</b> {Alerte}<br>
    <b>Zone:</b> {Nom}<br>
    <b>Description:</b> {Description}<br>
    <b>Cas:</b> {Cas}
    """,
    "style": {"backgroundColor": "#262730", "color": "white"}
}

st.markdown(
    f"## 🌍 Carte des fournisseurs et crises géopolitiques – Portefeuille{'s' if len(ID_selected)>1 else ''} {', '.join(ID_selected)}"
)
st.caption("Visualisez les localisations de vos fournisseurs critiques ainsi que les zones de crises géopolitiques majeures pouvant impacter la chaîne d'approvisionnement Airbus.")

deck = pdk.Deck(
    layers=[zones_layer, suppliers_layer, text_layer],
    initial_view_state=pdk.ViewState(longitude=float(center_lon), latitude=float(center_lat), zoom=2.1),
    tooltip=tooltip
)

st.pydeck_chart(deck)
st.markdown(generate_legend(ID_selected), unsafe_allow_html=True)

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
