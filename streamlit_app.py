import streamlit as st
import os
import json
import folium
from pyproj import Transformer
from streamlit_folium import st_folium

st.set_page_config(page_title="Mapas con JSON ESRI", layout="wide")
st.title("🗺️ Visualizador de puntos desde archivos JSON")

# Ruta a los archivos JSON
json_dir = "data"
json_files = [f for f in os.listdir(json_dir) if f.endswith(".json")]

@st.cache_data
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

if not json_files:
    st.warning("No se encontraron archivos JSON en la carpeta 'data'.")
else:
    selected_file = st.selectbox("Selecciona un archivo:", json_files)
    json_path = os.path.join(json_dir, selected_file)
    data = load_json(json_path)

    features = data.get("features", [])

    if not features:
        st.warning("El archivo no contiene 'features'.")
    else:
        # Convertir coordenadas de PROJCS a WGS84
        transformer = Transformer.from_crs(
            "PROJCS[\"Argentina_GKBsAs\",GEOGCS[\"GCS_Campo_Inchauspe\",DATUM[\"D_Campo_Inchauspe\",SPHEROID[\"International_1924\",6378388.0,297.0]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Transverse_Mercator\"],PARAMETER[\"False_Easting\",100000.0],PARAMETER[\"False_Northing\",100000.0],PARAMETER[\"Central_Meridian\",-58.4627],PARAMETER[\"Scale_Factor\",0.999998],PARAMETER[\"Latitude_Of_Origin\",-34.6297166],UNIT[\"Meter\",1.0]]",
            "EPSG:4326",
            always_xy=True
        )

        # Crear mapa con fondo claro
        m = folium.Map(location=[-34.6, -58.4], zoom_start=12, tiles="CartoDB positron")

        for f in features:
            attr = f.get("attributes", {})
            geom = f.get("geometry", {})
            x, y = geom.get("x"), geom.get("y")

            if x is not None and y is not None:
                lon, lat = transformer.transform(x, y)

                popup_text = f"<b>{attr.get('nombre', '')}</b><br>{attr.get('calle', '')} {attr.get('altura', '')}<br>{attr.get('barrio', '')}"
                folium.Marker(
                    location=[lat, lon],
                    popup=popup_text,
                    tooltip=attr.get("objeto", "Punto")
                ).add_to(m)

        # Mostrar mapa
        st_folium(m, width=1000, height=600, key="mapa")
