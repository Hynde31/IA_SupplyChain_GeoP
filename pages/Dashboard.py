import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Dashboard Supply Chain", layout="wide")

# ---------- 1. KPI Portefeuille ----------
st.title("KPI Portefeuille - Supply Chain")

# Données fictives pour l'exemple (à remplacer par tes requêtes réelles)
nb_mrp = 5
nb_fournisseurs = 8
nb_risque = 2
otd_moyen = 94.2
score_risque_moyen = 1.8
ruptures_cours = 1
dual_sourcing_pct = 65
nb_pays = 6

kpi1, kpi2, kpi3, kpi4, kpi5, kpi6, kpi7, kpi8 = st.columns(8)
kpi1.metric("MRP codes suivis", nb_mrp)
kpi2.metric("Fournisseurs actifs", nb_fournisseurs)
kpi3.metric("Sites à risque élevé", nb_risque)
kpi4.metric("On-Time Delivery", f"{otd_moyen}%")
kpi5.metric("Ruptures en cours", ruptures_cours)
kpi6.metric("Score risque moyen", f"{score_risque_moyen:.2f}")
kpi7.metric("Dual sourcing", f"{dual_sourcing_pct}%")
kpi8.metric("Pays couverts", nb_pays)

st.divider()

# ---------- 2. Carte interactive ----------
st.subheader("Carte des fournisseurs & zones à risque géopolitique")
# Données de localisation fictives pour la carte
carte_data = pd.DataFrame({
    "lat": [48.866667, 52.520008, 41.902782, 51.165691, 40.416775, 34.052235],
    "lon": [2.333333, 13.404954, 12.496366, 10.451526, -3.703790, -118.243683],
    "Fournisseur": [
        "Valeo", "Bosch", "Magneti Marelli", "Continental", "Gestamp", "Lear Corp."
    ],
    "Ville": [
        "Paris", "Berlin", "Rome", "Hanovre", "Madrid", "Los Angeles"
    ],
    "Risque": ["Faible", "Élevé", "Moyen", "Élevé", "Faible", "Moyen"]
})
st.map(carte_data)

st.divider()

# ---------- 3. Vue Approvisionneur (MRP x Fournisseur) ----------
st.header("Vision Approvisionneur : Statuts MRP / Fournisseurs")

# Exemple de structure MRP codes, chaque MRP code ayant plusieurs fournisseurs
# (Remplace par tes vraies données)
df_mrp_fourn = pd.DataFrame([
    {
        "MRP Code": "MRP001",
        "Désignation": "Moteur électrique",
        "Fournisseur": "Valeo",
        "Site": "Paris",
        "Contact": "contact@valeo.com",
        "Stock Jours": 4,
        "Retards (j)": 0,
        "OTD": "98%",
        "Dual sourcing": "Oui",
        "Criticité": "Haute",
        "ALERTE": ""
    },
    {
        "MRP Code": "MRP001",
        "Désignation": "Moteur électrique",
        "Fournisseur": "Bosch",
        "Site": "Berlin",
        "Contact": "logistique@bosch.com",
        "Stock Jours": 2,
        "Retards (j)": 2,
        "OTD": "84%",
        "Dual sourcing": "Oui",
        "Criticité": "Haute",
        "ALERTE": "⚠️ Stock bas & Retard"
    },
    {
        "MRP Code": "MRP002",
        "Désignation": "Calculateur moteur",
        "Fournisseur": "Continental",
        "Site": "Hanovre",
        "Contact": "supply@continental.com",
        "Stock Jours": 6,
        "Retards (j)": 0,
        "OTD": "99%",
        "Dual sourcing": "Non",
        "Criticité": "Très haute",
        "ALERTE": ""
    },
    {
        "MRP Code": "MRP003",
        "Désignation": "Batterie lithium",
        "Fournisseur": "Magneti Marelli",
        "Site": "Rome",
        "Contact": "appro@marelli.com",
        "Stock Jours": 3,
        "Retards (j)": 1,
        "OTD": "90%",
        "Dual sourcing": "Oui",
        "Criticité": "Haute",
        "ALERTE": "⚠️ Retard"
    },
    {
        "MRP Code": "MRP004",
        "Désignation": "Châssis",
        "Fournisseur": "Gestamp",
        "Site": "Madrid",
        "Contact": "espana@gestamp.com",
        "Stock Jours": 8,
        "Retards (j)": 0,
        "OTD": "96%",
        "Dual sourcing": "Oui",
        "Criticité": "Moyenne",
        "ALERTE": ""
    },
    {
        "MRP Code": "MRP004",
        "Désignation": "Châssis",
        "Fournisseur": "Lear Corp.",
        "Site": "Los Angeles",
        "Contact": "us@lear.com",
        "Stock Jours": 5,
        "Retards (j)": 0,
        "OTD": "97%",
        "Dual sourcing": "Oui",
        "Criticité": "Moyenne",
        "ALERTE": ""
    },
    {
        "MRP Code": "MRP005",
        "Désignation": "Connecteurs",
        "Fournisseur": "Delphi",
        "Site": "Luxembourg",
        "Contact": "lux@delphi.com",
        "Stock Jours": 1,
        "Retards (j)": 3,
        "OTD": "82%",
        "Dual sourcing": "Non",
        "Criticité": "Haute",
        "ALERTE": "⚠️ Rupture imminente"
    },
    {
        "MRP Code": "MRP002",
        "Désignation": "Calculateur moteur",
        "Fournisseur": "Valeo",
        "Site": "Paris",
        "Contact": "contact@valeo.com",
        "Stock Jours": 5,
        "Retards (j)": 0,
        "OTD": "97%",
        "Dual sourcing": "Non",
        "Criticité": "Très haute",
        "ALERTE": ""
    },
])

# Pour la lisibilité, on affiche par MRP puis fournisseur
st.dataframe(
    df_mrp_fourn[
        ["MRP Code", "Désignation", "Fournisseur", "Site", "Contact", "Stock Jours", "Retards (j)", "OTD", "Dual sourcing", "Criticité", "ALERTE"]
    ],
    use_container_width=True,
    hide_index=True
)

# ----------- 4. Alertes géopolitiques -----------
st.divider()
st.header("Alertes géopolitiques actives (liées au portefeuille)")

geo_alerts = [
    {"MRP Code": "MRP004", "Fournisseur": "Gestamp", "Zone": "Espagne", "Impact": "Blocage temporaire des routes"},
    {"MRP Code": "MRP001", "Fournisseur": "Bosch", "Zone": "Allemagne", "Impact": "Tensions politiques et logistiques"}
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
        st.switch_page("app.py")
with col2:
    if st.button("Veille géopolitique ➡️"):
        st.switch_page("pages/GeopoliticalNews.py")
