import base64
import json
import pandas as pd
from PIL import Image
import folium
from folium import Map, GeoJson, Choropleth, Marker, CircleMarker, TileLayer, GeoJsonTooltip, Tooltip, Popup, Icon, IFrame, Html, FeatureGroup

df = pd.read_excel('MT Base consolidada.xlsx')
df_articulos = pd.read_excel('Tesis Revisión Bibliográfica.xlsx')
with open('Casanare_municipios.geojson', encoding="utf8") as f:
    casanare_mapa = json.loads(f.read())
    
basemaps = {
    'Google Satellite': TileLayer(
        tiles = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr = 'Google',
        name = 'Google Satellite',
        overlay = False,
        control = True,
        show=True
    ),
    'Google Terrain': TileLayer(
        tiles = 'https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}',
        attr = 'Google',
        name = 'Google Terrain',
        overlay = False,
        control = True,
        show=False
    )
}

df = df[(df['Presencia_trypanosoma'] == 1) & (df['Organismos'] == 'Murcielago')]
df_resumen = df.groupby(['Sitio_de_colecta', 'W', 'N', 'Especie_12S']).agg({'Nombre muestra': 'count'}).reset_index().rename(columns={'N': 'Latitud', 'W': 'Longitud', 'Especie_12S': 'Especie', 'Nombre muestra': 'Cantidad'})
df_resumen = df_resumen[df_resumen['Cantidad'] != 0]

color_especie = {'Carollia perspicillata': '#b2df8a', 'Glossophaga soricina': '#33a02c', 'Micronycteris brachyotis': '#fb9a99', 'Myotis brandtii': '#e31a1c',
                 'Phyllostomus hastatus': '#fdbf6f', 'Anoura caudifer': '#a6cee3', 'Saccopteryx leptura': '#ff7f00', 'Carollia brevicauda': '#1f78b4',
                'Vampyrum spectrum': '#cab2d6'}

hospedero_map = Map(location=[5.190831, -72.322258], tiles=None, zoom_start=9)

basemaps['Google Satellite'].add_to(hospedero_map)
basemaps['Google Terrain'].add_to(hospedero_map)
# TileLayer('Stamen Terrain', name='Stamen Terrain', overlay=False, show=False).add_to(hospedero_map)

style = {'fillColor': '#FFFFFF', 'color': '#FFFFFF', "weight": 3, 'fillOpacity': 0.05}
GeoJson(casanare_mapa, name = 'Municipios de Casanare', overlay = True, style_function=lambda x: style, tooltip=GeoJsonTooltip(fields=['MPIO_CNMBR'], aliases=['MUNICIPIO'])).add_to(hospedero_map)

feature_articulos = FeatureGroup('Publicaciones', show=True)
for index, row in df_articulos.iterrows():
    
    html_popup = """
    <h2><b>{}</b></h2>
    <h4><i>{}</i></h4>
    <p>{}</p>
    <p><b>Secuenciación:</b> {}</p>
    <p><b>Especie(s):</b> <i>{}</i></p>
    """.format
    iframe = IFrame(html_popup(row['Articulo'], row['Autor'], row['Fecha'], row['Secuenciación'], row['Trypanosoma']), width=500, height=300, ratio='1%')
    popup = Popup(iframe, max_width=2650)
    
    html_tooltip = """
    <h4><i>{}</i></h4>
    <p>Click para más información</p>
    """.format
    
    feature_articulos.add_child(Marker([row['Latitud'], row['Longitud ']], popup=popup, tooltip=html_tooltip(row['Cita']), icon=Icon(color='red', icon='info-sign')))

feature_articulos.add_to(hospedero_map)

for especie in df_resumen.Especie.unique():
    temp_df = df_resumen[df_resumen['Especie'] == especie]
#     show_especie = True if especie == 'Carollia perspicillata' else False
    feature_group = FeatureGroup(especie, show=False)
    
    html_tooltip = """
    <h4><i>{}</i></h4>
    <h5><b>Cantidad:</b> {}</h5>
    """.format
    
    temp_df.apply(lambda row: feature_group.add_child(CircleMarker([row['Latitud'], row['Longitud']], radius=5*row['Cantidad'], tooltip=Tooltip(html_tooltip(especie, row['Cantidad'])), color=color_especie[especie], fill=True)), axis=1)
    feature_group.add_to(hospedero_map)
    
folium.LayerControl().add_to(hospedero_map)
hospedero_map.save('index.html')