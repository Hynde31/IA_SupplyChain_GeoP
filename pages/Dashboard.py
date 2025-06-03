import streamlit as st
import pandas as pd
from suppliers_data import SUPPLIERS
from utils import risk_gauge, kpi_card

st.set_page_config(page_title="Dashboard", layout="wide")
st.title("Dashboard – Portefeuille fournisseur")

# Navigation vers les autres pages
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("⬅️ Accueil"):
        st.switch_page("pages/Accueil.py")
with col2:
    if st.button("Voir les actualités ➡️"):
        st.switch_page("pages/GeopoliticalNews.py")

mrp_codes = st.session_state.get("mrp_codes", [])
if not mrp_codes:
    st.warning("Vous devez d'abord définir votre portefeuille MRP sur la page Accueil.")
    st.stop()

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
st.header
