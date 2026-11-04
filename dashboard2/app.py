import streamlit as st
import folium
from streamlit_folium import st_folium
import requests

st.set_page_config(layout="wide")
API = "http://localhost:8000/api/v1"

STATUS_COLOR = {"green": "green", "yellow": "orange", "red": "red"}

sewers = requests.get(f"{API}/sewers").json()

m = folium.Map(location=[22.72, 75.87], zoom_start=13)  # centered on your deployment area

for s in sewers:
    popup_html = f"""
    <b>{s['name']} ({s['node_id']})</b><br>
    Status: <b>{s['status'].upper()}</b><br>
    Water level: {s['water_level_mm']} mm<br>
    d/D ratio: {s['water_level_mm']/s['pipe_diameter_mm']:.2f}<br>
    Last update: {s['ts']}<br>
    {'⚠️ Blockage detected' if s['ir_blocked'] else ''}
    """
    folium.CircleMarker(
        location=[s['latitude'], s['longitude']],
        radius=10,
        color=STATUS_COLOR[s['status']],
        fill=True,
        fill_color=STATUS_COLOR[s['status']],
        fill_opacity=0.85,
        popup=folium.Popup(popup_html, max_width=250),
    ).add_to(m)

st.title("RTSMS — Live Sewer Network Map")
st_folium(m, width=1200, height=600)

# Sidebar: filter + summary counts
with st.sidebar:
    st.metric("Normal", sum(1 for s in sewers if s['status']=='green'))
    st.metric("Caution", sum(1 for s in sewers if s['status']=='yellow'))
    st.metric("Risk", sum(1 for s in sewers if s['status']=='red'))

# Below map: recent events table
st.subheader("Recent Alerts")
events = requests.get(f"{API}/events").json()
st.dataframe(events)