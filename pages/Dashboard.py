import streamlit as st
import pandas as pd
from suppliers_data import SUPPLIERS
from utils import risk_gauge, kpi_card

st.set_page_config(page_title="Dashboard Supply Chain", layout="wide")

# 0. Sélection du portefeuille
mrp_codes = st.session_state.get("mrp_codes", [])
if not mrp_codes:
    st.warning("Vous devez d'abord définir votre portefeuille MRP sur la page Accueil.")
    st.stop()

# 1. Construction du DataFrame principal
def flatten_suppliers(suppliers, mrp_codes):
    rows = []
    for s in suppliers:
        if s["mrp_code"] not in mrp_codes:
            continue
        for site in s["sites"]:
            rows.append({
                "MRP Code": s["mrp_code"],
                "Désignation": s["component"],
                "Fournisseur": s["name"],
                "Criticité": s["criticality"],
                "Dual sourcing": "Oui" if s["dual_sourcing"] else "Non",
                "Site": site["city"],
                "Pays": site["country"],
                "Stock Jours": site["stock_days"],
                "OTD (%)": site["on_time_delivery"],
                "Lead time (j)": site["lead_time"],
                "Incidents": site["incidents"],
                "latitude": site["lat"],
                "longitude": site["lon"],
            })
    return pd.DataFrame(rows)

df = flatten_suppliers(SUPPLIERS, mrp_codes)

if df.empty:
    st.info("Aucun fournisseur trouvé pour les codes MRP sélectionnés.")
    st.stop()

# 2. Calculs des indicateurs (KPI)
nb_mrp = df["MRP Code"].nunique()
nb_fournisseurs = df["Fournisseur"].nunique()
nb_pays = df["Pays"].nunique()
nb_sites_risque = ((df["OTD (%)"] < 85) | (df["Stock Jours"] < 5)).sum()
otd_moyen = round(df["OTD (%)"].mean(), 1)
score_risque_moyen = (
    (1 - df["OTD (%)"]/100)
    + (df["Incidents"]/10)
    + (1 - df["Stock Jours"]/60)*0.5
    + (df["Lead time (j)"]/150)*0.5
).mean()
ruptures_cours = (df["Stock Jours"] < 2).sum()
dual_sourcing_pct = round(100 * (df["Dual sourcing"]=="Oui").sum() / len(df), 1) if len(df) > 0 else 0

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

# 4. Carte interactive : fournisseurs + zones géopolitiques
st.subheader("Carte des fournisseurs & zones à risque géopolitique")
zones_geopol = pd.DataFrame([
    {"label": "Mer Rouge (Blocage maritime)", "lat": 16.3, "lon": 42.6},
    {"label": "Ukraine (Conflit armé)", "lat": 48.4, "lon": 31.2},
    {"label": "Taïwan (Tensions Chine/USA)", "lat": 23.7, "lon": 121.0},
])
# Renommage pour concat
map_fournisseurs = df[["latitude", "longitude"]].rename(columns={"latitude": "lat", "longitude": "lon"})
map_fournisseurs["label"] = "Fournisseur"
map_total = pd.concat([map_fournisseurs, zones_geopol], ignore_index=True)
st.map(map_total[["lat", "lon"]])
st.caption(":red[⚠️ Les points hors fournisseurs sont les zones géopolitiques à risque.]")

st.divider()

st.header("Vision Approvisionneur : Statuts MRP / Fournisseurs")
df["ALERTE"] = ""
df.loc[df["Stock Jours"] < 5, "ALERTE"] += "⚠️ Stock bas "
df.loc[df["OTD (%)"] < 85, "ALERTE"] += "⚠️ Retard "
df.loc[df["Stock Jours"] < 2, "ALERTE"] += "❗ Rupture imminente "
st.dataframe(
    df[
        ["MRP Code", "Désignation", "Fournisseur", "Site", "Pays", "Stock Jours", "OTD (%)", "Dual sourcing", "Criticité", "Lead time (j)", "Incidents", "ALERTE"]
    ],
    use_container_width=True,
    hide_index=True
)

st.divider()
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("🏠 Accueil"):
        st.switch_page("Accueil.py")
with col2:
    if st.button("Veille géopolitique ➡️"):
        st.switch_page("GeopoliticalNews.py")
