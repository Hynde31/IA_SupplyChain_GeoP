import streamlit as st
import pandas as pd
import pydeck as pdk
from suppliers_data import SUPPLIERS
from utils import risk_gauge, kpi_card

st.set_page_config(page_title="Dashboard", layout="wide")
st.title("Dashboard – Portefeuille fournisseur")

mrp_codes = st.session_state.get("mrp_codes", [])
if not mrp_codes:
    st.warning("Vous devez d'abord définir votre portefeuille MRP sur la page Accueil.")
    if st.button("⬅️ Retour Accueil"):
        st.switch_page("pages/Accueil.py")
    st.stop()

# Flatten supplier data for selected MRP codes
def flatten_suppliers(suppliers, mrp_codes):
    rows = []
    for s in suppliers:
        if s["mrp_code"] not in mrp_codes:
            continue
        for site in s["sites"]:
            rows.append({
                "MRP": s["mrp_code"],
                "Supplier": s["name"],
                "Component": s["component"],
                "Criticality": s["criticality"],
                "Dual Sourcing": "Yes" if s["dual_sourcing"] else "No",
                "Site City": site["city"],
                "Country": site["country"],
                "latitude": site["lat"],
                "longitude": site["lon"],
                "Stock Days": site["stock_days"],
                "Lead Time": site["lead_time"],
                "On-Time Delivery (%)": site["on_time_delivery"],
                "Incidents": site["incidents"]
            })
    return pd.DataFrame(rows)

df = flatten_suppliers(SUPPLIERS, mrp_codes)

# Simule des conflits géopolitiques (remplace cette fonction par la tienne si tu as un flux live)
def get_geopolitical_impacts_now():
    # Exemple Ukraine, Mer Rouge, Israël
    return [
        {
            "zone": "Est Ukraine",
            "lat": 48.5,
            "lon": 37.5,
            "impact": 1.0,
            "titre": "Conflit armé"
        },
        {
            "zone": "Mer Rouge",
            "lat": 15.8,
            "lon": 41.8,
            "impact": 0.7,
            "titre": "Attaques route maritime"
        },
        {
            "zone": "Proche Israël",
            "lat": 31.5,
            "lon": 34.8,
            "impact": 0.9,
            "titre": "Tensions militaires"
        }
    ]

conflicts = get_geopolitical_impacts_now()
df_conflict = pd.DataFrame(conflicts)

# --------------- MAP EN HAUT -----------------
supplier_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position="[longitude, latitude]",
    get_fill_color="[40, 120, 255, 200]",
    get_radius=35000,
    pickable=True,
    auto_highlight=True,
    radius_min_pixels=5,
    radius_max_pixels=15,
)

conflict_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_conflict,
    get_position="[lon, lat]",
    get_fill_color="[255, 60, 60, 180]",
    get_radius="impact * 100000",
    pickable=True,
    auto_highlight=True,
    radius_min_pixels=10,
    radius_max_pixels=60,
)

view_state = pdk.ViewState(
    latitude=df["latitude"].mean() if not df.empty else 30,
    longitude=df["longitude"].mean() if not df.empty else 10,
    zoom=2.6,
    pitch=0,
)

st.subheader("Carte interactive : sites fournisseurs & conflits géopolitiques en temps réel")
st.pydeck_chart(
    pdk.Deck(
        layers=[supplier_layer, conflict_layer],
        initial_view_state=view_state,
        tooltip={
            "html": "<b>Type:</b> {Supplier} {zone}<br/><b>Ville:</b> {Site City}<br/><b>Pays:</b> {Country} <br/><b>Incident:</b> {titre}",
            "style": {"color": "white"},
        }
    )
)

# --------------- KPI & TABLEAUX -----------------
if not df.empty:
    # Calcul du score de risque et niveau
    df["Risk Score"] = (1 - df["On-Time Delivery (%)"]/100) \
                       + (df["Incidents"]/10) \
                       + (1 - df["Stock Days"]/60)*0.5 \
                       + (df["Lead Time"]/150)*0.5
    df["Risk Level"] = pd.cut(df["Risk Score"], bins=[-float("inf"),0.5,1,2], labels=["Low","Medium","High"])

    st.header("KPI globaux du portefeuille")
    col1, col2, col3, col4 = st.columns(4)
    kpi_card("Fournisseurs actifs", df["Supplier"].nunique(), color="#2876D3")
    kpi_card("Pays couverts", df["Country"].nunique(), color="#2CA977")
    late_or_missing = (df["On-Time Delivery (%)"] < 85).sum() + (df["Stock Days"] < 5).sum()
    kpi_card("Risques de retard/manquant", late_or_missing, color="#F4C542", helptext="Nb sites à risque élevé de rupture ou retard")
    kpi_card("Incidents cumulés", int(df["Incidents"].sum()), color="#C92A2A")

    st.subheader("Niveau de risque global du portefeuille")
    risk_gauge(df["Risk Score"].mean(), label="Risk Score moyen portefeuille")

    st.subheader("Tableau détaillé des sites fournisseurs")
    st.dataframe(df, use_container_width=True)
else:
    st.warning("Aucun site fournisseur dans ce portefeuille.")

# Navigation boutons
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("⬅️ Accueil"):
        st.switch_page("pages/Accueil.py")
with col2:
    if st.button("Page suivante ➡️"):
        st.switch_page("pages/GeopoliticalNews.py")
