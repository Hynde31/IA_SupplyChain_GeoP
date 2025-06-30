import streamlit as st
import pandas as pd
from ai_models import recommend_action, geopolitical_risk_score
from geo_zones import ZONES_GEO

st.set_page_config(page_title="Recommandations IA", layout="wide")
st.title("🤖 Recommandations IA pour la résilience Supply Chain")

@st.cache_data
def load_suppliers(path="mapping_fournisseurs.csv"):
    df = pd.read_csv(path)
    df = df.fillna("")
    return df

df_sup = load_suppliers()
if df_sup.empty:
    st.warning("Aucun fournisseur.")
    st.stop()

df_sup["Score risque géopolitique"] = df_sup.apply(lambda r: geopolitical_risk_score(r, ZONES_GEO), axis=1)
df_sup["Recommandation IA"] = df_sup.apply(lambda r: recommend_action(r, ZONES_GEO), axis=1)

st.dataframe(
    df_sup[["Portefeuille", "Fournisseur", "Pays", "Ville", "Score risque géopolitique", "Recommandation IA"]],
    use_container_width=True,
    hide_index=True
)
