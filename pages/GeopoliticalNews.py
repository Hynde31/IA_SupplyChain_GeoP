import streamlit as st
import pandas as pd
from geo_zones import ZONES_GEO

st.title("📰 Synthèse des zones géopolitiques")

df_geo = pd.DataFrame(ZONES_GEO)

# Vérifier colonnes existantes et les adapter
cols_to_show = [col for col in ["Nom", "Description", "Impact"] if col in df_geo.columns]

if cols_to_show:
    st.dataframe(df_geo[cols_to_show], use_container_width=True)
else:
    st.warning("Structure des données zones géopolitiques incorrecte.")

