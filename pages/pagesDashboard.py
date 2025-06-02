import streamlit as st
import pandas as pd
from suppliers_data import SUPPLIERS
from utils import risk_gauge, kpi_card

st.title("Dashboard – Portefeuille fournisseur")

mrp_codes = st.session_state.get("mrp_codes", [])
if not mrp_codes:
    st.warning("Vous devez d'abord définir votre portefeuille MRP sur la page Accueil.")
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

# Calcul du score de risque et niveau
df["Risk Score"] = (1 - df["On-Time Delivery (%)"]/100) \
                   + (df["Incidents"]/10) \
                   + (1 - df["Stock Days"]/60)*0.5 \
                   + (df["Lead Time"]/150)*0.5
df["Risk Level"] = pd.cut(df["Risk Score"], bins=[-float("inf"),0.5,1,2], labels=["Low","Medium","High"])

# KPI visibles dès l'entrée
st.header("KPI globaux du portefeuille")
col1, col2, col3, col4 = st.columns(4)
kpi_card("Fournisseurs actifs", df["Supplier"].nunique(), color="#2876D3")
kpi_card("Pays couverts", df["Country"].nunique(), color="#2CA977")
late_or_missing = (df["On-Time Delivery (%)"] < 85).sum() + (df["Stock Days"] < 5).sum()
kpi_card("Risques de retard/manquant", late_or_missing, color="#F4C542", helptext="Nb sites à risque élevé de rupture ou retard")
kpi_card("Incidents cumulés", int(df["Incidents"].sum()), color="#C92A2A")

# Jauge score de RISQUE global portefeuille
st.subheader("Niveau de risque global du portefeuille")
risk_gauge(df["Risk Score"].mean(), label="Risk Score moyen portefeuille")

# Tableau détaillé
st.subheader("Tableau détaillé des sites fournisseurs")
st.dataframe(df, use_container_width=True)

# Carte des sites
st.subheader("Carte interactive des sites fournisseurs")
if not df.empty and df[["latitude", "longitude"]].notnull().all().all():
    st.map(df[["latitude", "longitude"]])
else:
    st.info("Aucun site localisé pour ce portefeuille.")