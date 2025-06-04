import streamlit as st
import pandas as pd
from suppliers_data import SUPPLIERS
from utils import risk_gauge, kpi_card

st.set_page_config(page_title="Dashboard Supply Chain", layout="wide")

# ---------- Récupération des MRP codes sélectionnés ----------
mrp_codes = st.session_state.get("mrp_codes", [])
if not mrp_codes:
    st.warning("Vous devez d'abord définir votre portefeuille MRP sur la page Accueil.")
    st.stop()

# ---------- Construction DataFrame principal à partir de suppliers_data.py ----------
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
                "Retards (j)": 0,  # optionnel, non fourni, à calculer si tu as l'info
                "OTD": f"{site['on_time_delivery']}%",
                "OTD_num": site["on_time_delivery"],
                "Lead time (j)": site["lead_time"],
                "Incidents": site["incidents"],
                "latitude": site["lat"],
                "longitude": site["lon"],
            })
    return pd.DataFrame(rows)

df = flatten_suppliers(SUPPLIERS, mrp_codes)

# ---------- Calcul KPI dynamiques ----------
nb_mrp = df["MRP Code"].nunique()
nb_fournisseurs = df["Fournisseur"].nunique()
nb_pays = df["Pays"].nunique()
nb_sites_risque = ((df["OTD_num"] < 85) | (df["Stock Jours"] < 5)).sum()
otd_moyen = round(df["OTD_num"].mean(), 1) if not df.empty else 0
score_risque_moyen = (
    (1 - df["OTD_num"]/100)
    + (df["Incidents"]/10)
    + (1 - df["Stock Jours"]/60)*0.5
    + (df["Lead time (j)"]/150)*0.5
).mean() if not df.empty else 0
ruptures_cours = (df["Stock Jours"] < 2).sum()
dual_sourcing_pct = round(100 * (df["Dual sourcing"]=="Oui").sum() / len(df), 1) if len(df) > 0 else 0

# ---------- 1. KPI Portefeuille ----------
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

# ---------- 2. Carte interactive ----------
st.subheader("Carte des fournisseurs & zones à risque géopolitique")
if not df.empty and df[["latitude", "longitude"]].notnull().all().all():
    st.map(df[["latitude", "longitude"]])
else:
    st.info("Aucun site localisé pour ce portefeuille.")

st.divider()

# ---------- 3. Vue Approvisionneur (MRP x Fournisseur) ----------
st.header("Vision Approvisionneur : Statuts MRP / Fournisseurs")
# Ajout des alertes
df["ALERTE"] = ""
df.loc[df["Stock Jours"] < 5, "ALERTE"] += "⚠️ Stock bas "
df.loc[df["OTD_num"] < 85, "ALERTE"] += "⚠️ Retard "
df.loc[df["Stock Jours"] < 2, "ALERTE"] += "❗ Rupture imminente "

st.dataframe(
    df[
        ["MRP Code", "Désignation", "Fournisseur", "Site", "Pays", "Stock Jours", "OTD", "Dual sourcing", "Criticité", "Lead time (j)", "Incidents", "ALERTE"]
    ],
    use_container_width=True,
    hide_index=True
)

# ----------- 4. Alertes géopolitiques (placeholders dynamiques) -----------
st.divider()
st.header("Alertes géopolitiques actives (liées au portefeuille)")
# Cette section est à brancher sur tes vrais résultats de veille géopolitique
geo_alerts = [
    # Exemples à remplacer par une vraie détection
    {"MRP Code": row["MRP Code"], "Fournisseur": row["Fournisseur"], "Zone": row["Pays"], "Impact": "Exemple d'alerte"}
    for _, row in df.iterrows() if row["Pays"] in ["Tunisie", "USA", "Allemagne"]  # à adapter selon détection réelle
]
if geo_alerts:
    for alert in geo_alerts:
        st.warning(
            f"⚠️ {alert['Fournisseur']} (MRP {alert['MRP Code']}) exposé ({alert['Zone']})\n> Impact : {alert['Impact']}"
        )
else:
    st.success("Aucune alerte géopolitique active sur votre portefeuille.")

# ----------- Navigation -----------
st.divider()
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("🏠 Accueil"):
        st.switch_page("pages/Accueil.py")
with col2:
    if st.button("Veille géopolitique ➡️"):
        st.switch_page("pages/GeopoliticalNews.py")
