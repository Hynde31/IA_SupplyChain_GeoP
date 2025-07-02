import streamlit as st
import pandas as pd
from ai_models import recommend_actions, geopolitical_risk_score
from geo_zones import ZONES_GEO

@st.cache_data
def load_suppliers(path="mapping_fournisseurs.csv"):
    return pd.read_csv(path).fillna("")

df = load_suppliers()

if df.empty:
    st.warning("Aucun fournisseur chargé.")
    st.stop()

st.title("🤖 IA - Recommandations stratégiques")

# Calcul des risques si non présent
if "Score risque géopolitique" not in df.columns:
    df["Score risque géopolitique"] = df.apply(lambda r: geopolitical_risk_score(r, ZONES_GEO), axis=1)

recs = recommend_actions(df)

for r in recs:
    st.write(r)
