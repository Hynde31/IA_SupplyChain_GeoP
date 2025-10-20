import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
import traceback

# Imports
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
# Ne pas st.stop() ici pour permettre d'afficher les zones même si aucun fournisseur
if df_sup.empty:
    st.warning("Le fichier mapping_fournisseurs.csv est vide ou introuvable. Les zones seront tout de même affichées si définies.")

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

# 3. Géolocalisation fournisseurs (cities_coords stocke (lat, lon))
df_sup["Ville"] = df_sup["Ville"].astype(str).str.strip()
df_sup["Latitude"] = df_sup["Ville"].map(lambda v: cities_coords.get(v, (np.nan, np.nan))[0])
df_sup["Longitude"] = df_sup["Ville"].map(lambda v: cities_coords.get(v, (np.nan, np.nan))[1])

# 4. Score risque géopolitique
if not df_sup.empty:
    df_sup["Score risque géopolitique"] = df_sup.apply(lambda r: geopolitical_risk_score(r, ZONES_GEO), axis=1)
    df_sup["Score (%)"] = (df_sup["Score risque géopolitique"] * 100).round(1)
    df_sup["Score_pct"] = df_sup["Score (%)"]  # colonne sans espaces pour tooltip
    df_sup["Alerte"] = df_sup["Score risque géopolitique"].apply(
        lambda s: "🟥 Critique" if s >= 0.7 else ("🟧 Surveille" if s >= 0.5 else "🟩 OK")
    )
else:
    # Colonnes vides si pas de fournisseurs sélectionnés
    df_sup["Score risque géopolitique"] = pd.Series(dtype=float)
    df_sup["Score (%)"] = pd.Series(dtype=float)
    df_sup["Score_pct"] = pd.Series(dtype=float)
    df_sup["Alerte"] = pd.Series(dtype=str)

# Colonne Portefeuille stable pour tooltip
df_sup["Portefeuille"] = df_sup[col_portefeuille] if col_portefeuille else ""

#  --- Couleurs : normaliser vers [r,g,b,a] ---
def ensure_rgba(col):
    if not isinstance(col, (list, tuple)):
        return [200, 200, 200, 255]
    col = list(col)
    if len(col) == 3:
        col.append(255)
    return [int(col[0]), int(col[1]), int(col[2]), int(col[3])]

color_dict = ID_colors if isinstance(ID_colors, dict) else {}
df_sup["Couleur ID"] = df_sup[col_portefeuille].apply(
    lambda x: ensure_rgba(color_dict.get(x, color_dict.get("DEFAULT", [200,200,200])))
)
df_sup["type"] = "Fournisseur"
df_sup["label"] = df_sup.get("Fournisseur", df_sup.get(col_portefeuille, ""))

# 5. Préparation zones géopolitiques
df_geo = pd.DataFrame(ZONES_GEO).copy()
# s'assurer des colonnes
df_geo["Latitude"] = pd.to_numeric(df_geo.get("Latitude"), errors="coerce")
df_geo["Longitude"] = pd.to_numeric(df_geo.get("Longitude"), errors="coerce")
df_geo["Couleur ID"] = df_geo["Couleur"].apply(ensure_rgba)
df_geo["type"] = "Crise géopolitique"
df_geo["Fournisseur"] = ""
df_geo["Pays"] = df_geo["Nom"]
df_geo["label"] = df_geo["Nom"]
# colonne Portefeuille vide pour zones (évite KeyError dans tooltip)
df_geo["Portefeuille"] = ""

# 6. Construire coordonnées au format attendu par pydeck : [lon, lat]
# Pour fournisseurs
if "Latitude" in df_sup.columns and "Longitude" in df_sup.columns:
    df_sup["Latitude"] = pd.to_numeric(df_sup["Latitude"], errors="coerce")
    df_sup["Longitude"] = pd.to_numeric(df_sup["Longitude"], errors="coerce")
    df_sup["coordinates"] = df_sup.apply(
        lambda r: [float(r["Longitude"]), float(r["Latitude"])] if pd.notna(r["Latitude"]) and pd.notna(r["Longitude"]) else None,
        axis=1
    )
else:
    df_sup["coordinates"] = None

# Pour zones
df_geo["coordinates"] = df_geo.apply(
    lambda r: [float(r["Longitude"]), float(r["Latitude"])] if pd.notna(r["Latitude"]) and pd.notna(r["Longitude"]) else None,
    axis=1
)

# Option: injecter points de test pour vérifier affichage (décommenter si utile)
# test_points = False
# if test_points:
#     # Ajouter un point test pour vérifier l'affichage
#     df_sup = pd.concat([df_sup, pd.DataFrame([{
#         "Fournisseur": "TEST Rousset",
#         "Ville": "Rousset",
#         "Latitude": 43.4285,
#         "Longitude": 5.5872,
#         "coordinates": [5.5872, 43.4285],
#         "Couleur ID": ensure_rgba([57,106,177]),
#         "Portefeuille": "TEST",
#         "Score_pct": 12.3,
#         "Alerte": "🟩 OK",
#         "type": "Fournisseur",
#         "label": "TEST Rousset"
#     }])], ignore_index=True)

# 7. Préparer dataframes pour les layers (points valides seulement)
suppliers_layer_df = df_sup[df_sup["coordinates"].notna()].copy()
zones_layer_df = df_geo[df_geo["coordinates"].notna()].copy()

# Si aucun point fournisseur mais des zones présentes, on affichera au moins les zones
if suppliers_layer_df.empty and zones_layer_df.empty:
    st.warning("Aucun point géolocalisé à afficher. Vérifiez que les noms de villes dans le CSV correspondent aux clés de mapping.cities_coords.")
else:
    # Calculer centre à partir de tous les coords disponibles (zones + fournisseurs)
    all_coords = pd.concat([
        suppliers_layer_df[["coordinates"]].dropna().assign(lon=lambda d: d["coordinates"].map(lambda c: c[0]), lat=lambda d: d["coordinates"].map(lambda c: c[1])),
        zones_layer_df[["coordinates"]].dropna().assign(lon=lambda d: d["coordinates"].map(lambda c: c[0]), lat=lambda d: d["coordinates"].map(lambda c: c[1]))
    ], ignore_index=True)

    center_lat = float(all_coords["lat"].mean())
    center_lon = float(all_coords["lon"].mean())

    lat_min, lat_max = all_coords["lat"].min(), all_coords["lat"].max()
    lon_min, lon_max = all_coords["lon"].min(), all_coords["lon"].max()
    lat_span = lat_max - lat_min if pd.notna(lat_max) and pd.notna(lat_min) else 180
    lon_span = lon_max - lon_min if pd.notna(lon_max) and pd.notna(lon_min) else 360
    span = max(lat_span, lon_span)
    if span < 0.5:
        zoom = 6.0
    elif span < 3:
        zoom = 4.0
    elif span < 20:
        zoom = 3.0
    else:
        zoom = 2.1

    # Rayons
    suppliers_layer_df["radius"] = suppliers_layer_df.get("radius", 30000)
    if "Impact" in zones_layer_df.columns:
        zones_layer_df["radius"] = zones_layer_df["Impact"].apply(lambda x: max(80000, float(x) * 300000))
    else:
        zones_layer_df["radius"] = 200000

    # Layers (utilise la colonne 'coordinates')
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

    # Text labels : n'afficher que les labels des zones par défaut pour réduire le bruit
    text_df = zones_layer_df[["coordinates", "label", "Couleur ID"]].copy()
    # TextLayer prend aussi une position au format [lon, lat]
    text_layer = pdk.Layer(
        "TextLayer",
        data=text_df.assign(Longitude=text_df["coordinates"].map(lambda c: c[0]), Latitude=text_df["coordinates"].map(lambda c: c[1])).assign(coordinates=lambda d: d[["Longitude","Latitude"]].values.tolist()),
        get_position="coordinates",
        get_text="label",
        get_color="Couleur ID",
        get_size=14,
        get_alignment_baseline='"bottom"',
        pickable=False,
    )

    # Tooltip : utiliser colonnes "propres" (sans espaces) quand possible
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

    st.markdown(
        f"## 🌍 Carte des fournisseurs et crises géopolitiques – Portefeuille{'s' if len(ID_selected)>1 else ''} {', '.join(ID_selected)}"
    )
    st.caption("Visualisez les localisations de vos fournisseurs critiques ainsi que les zones de crises géopolitiques majeures pouvant impacter la chaîne d'approvisionnement Airbus.")

    deck = pdk.Deck(
        layers=[zones_layer, suppliers_layer, text_layer],
        initial_view_state=pdk.ViewState(longitude=center_lon, latitude=center_lat, zoom=zoom),
        tooltip=tooltip
    )
    st.pydeck_chart(deck)

# Afficher la légende
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
