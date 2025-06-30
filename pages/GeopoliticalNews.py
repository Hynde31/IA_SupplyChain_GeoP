import streamlit as st
from geo_zones import ZONES_GEO
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Veille géopolitique", layout="wide")

st.title("Veille géopolitique")
st.write("""
La veille géopolitique automatique est désactivée (aucune dépendance spaCy).  
Les zones affichées ci-dessous sont ajoutées manuellement par l'administrateur.
""")

df_geo = pd.DataFrame(ZONES_GEO)
if not df_geo.empty:
    st.dataframe(df_geo[["label", "Impact", "latitude", "longitude", "Couleur"]], use_container_width=True)
    # Mini-carte des zones
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_geo,
        get_position='[longitude, latitude]',
        get_color="Couleur",
        get_radius=50000,
        pickable=True,
        auto_highlight=True,
    )
    view_state = pdk.ViewState(
        longitude=float(df_geo["longitude"].mean()),
        latitude=float(df_geo["latitude"].mean()),
        zoom=2.5,
        pitch=0,
    )
    st.pydeck_chart(
        pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"html": "<b>Zone:</b> {label}<br><b>Impact:</b> {Impact}"}
        )
    )
else:
    st.info("Aucune zone géopolitique renseignée actuellement.")

st.divider()
st.page_link("pages/Accueil.py", label="⏪ Retour Accueil")
