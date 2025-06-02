import streamlit as st
import pandas as pd
from geo_news_nlp import get_news_impact_for_month
import pydeck as pdk

st.title("Veille géopolitique intelligente")

# Choix du mois/année
import datetime
now = datetime.datetime.now()
months = [f"{y}-{m:02d}" for y in range(now.year-1, now.year+1) for m in range(1, 13)]
selected_month = st.selectbox("Choisissez la période :", months[::-1], index=0)

news, impacts = get_news_impact_for_month(selected_month)

st.subheader("Actualités ayant un impact logistique")
for n in news:
    st.markdown(f"**{n['date']} — {n['title']}**  \n{n['summary']}")

st.subheader("Carte des zones à risque (impact géopolitique détecté)")
if impacts:
    df = pd.DataFrame(impacts)
    layer = pdk.Layer(
        "ScatterplotLayer",
        df,
        get_position='[lon, lat]',
        get_radius="impact * 30000 + 20000",
        get_fill_color="[255, 0, 0, 140]",
        pickable=True
    )
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=pdk.ViewState(latitude=35, longitude=20, zoom=1.2),
        layers=[layer]
    ))
else:
    st.info("Aucun impact détecté ce mois-ci.")
