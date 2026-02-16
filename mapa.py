import streamlit as st
import json
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="MAPA MC CHIAPAS 2026", layout="wide")

# --- LISTA DE MUNICIPIOS A RESALTAR ---
municipios_naranja = ['102', '61', '90', '59','77','19','52','65','31','109','27','23','97','17','99','57','34','108','106','96','40','82']

# --- 1. CARGA DE DATOS ---
@st.cache_data
def load_data():
    with open("MUNICIPIO.json", encoding='utf-8') as f:
        geojson_mun = json.load(f)
    
    # NUEVO: Carga del archivo de formas de SECCIONES
    with open("SECCION.json", encoding='utf-8') as f:
        geojson_secc = json.load(f)
    
    df_muni = pd.read_csv("tu_archivo.csv", encoding='utf-8-sig', dtype={'MUNICIPIO': str})
    df_muni.columns = df_muni.columns.str.strip()
    
    df_secc = pd.read_csv("SECCION.csv", encoding='utf-8-sig', dtype={'Cve Mpio': str, 'Secc': str})
    df_secc.columns = df_secc.columns.str.strip()
    
    return geojson_mun, geojson_secc, df_muni, df_secc

geojson_mun, geojson_secc, df_muni, df_secc = load_data()

# --- 2. ESTADO DE SELECCIÓN ---
if 'muni_id' not in st.session_state:
    st.session_state.muni_id = None

# --- 3. INTERFAZ ---
st.title("📊 Análisis Estratégico Chiapas")

if st.session_state.muni_id:
    #3.1 Extraer fila del municipio seleccionado
    info_muni = df_muni[df_muni['MUNICIPIO'] == st.session_state.muni_id].iloc[0]
    nombre_display = info_muni['NOMBRE MUNICIPIO']

    if st.button(f"⬅️ Regresar (Viendo: {nombre_display})"):
        st.session_state.muni_id = None
        st.rerun()

    #3.2 --- FILA 1: CUADROS INFORMATIVOS ---
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        with st.container(border=True):
            st.subheader("📖 INFORMACION MUNICIPAL")
            st.write(f"Municipio: **{nombre_display}**. Distrito Federal: **{info_muni['DISTRITO FEDERAL']}**. Distrito Local: **{info_muni['DISTRITO LOCAL']}**.")
                                                                    
    with c2:
        with st.container(border=True):
            st.subheader("📦 SECCIONES")
            st.write(f"Total: **{info_muni['SECCION']:,}**. Prioritarias: **{info_muni['SECCION PRIORITARIOS']:,}** ({info_muni['PORCENTAJE PRIORITARIO']}%).")
    
    with c3:
        with st.container(border=True):
            st.subheader("🏠 MANZANAS")
            st.write(f"Total: **{info_muni['MANZANA TOTAL']:,}**. Prioritarias: **{info_muni['MANZANA PRIORITARIA']:,}**.")
    
    with c4:
        with st.container(border=True):
            st.subheader("🎯 PARTICIPACION")
            st.write(f"L.N.: **{info_muni['LISTADO NOMINAL']}**. Participación: **{info_muni['PORCENTAJE PARTICIPACION CIUDADANA']}**%.")

    #3.3 --- FILA 2: MAPA DE SECCIONES (CAMBIO AQUÍ) Y TABLA ---
    col_mapa, col_tabla = st.columns([1.8, 1.2])

    with col_mapa:
        st.markdown(f"### 🗺️ Mapa Seccional de {nombre_display}")
        
        #3.3.1. FILTRO GeoJSON de secciones del municipio actual
        secciones_geojson_filtrado = {
            "type": "FeatureCollection",
            "features": [
                f for f in geojson_secc['features'] 
                if str(f['properties'].get('MUNICIPIO')) == st.session_state.muni_id
            ]
        }
        
        # 3.3.2 Calcular centros de cada sección para poner el número
        secciones_list = []
        for f in secciones_geojson_filtrado['features']:
            s_id = str(f['properties'].get('SECCION'))
            geom = f['geometry']
            
            #3.3.2.1 Lógica para obtener el centro del polígono
            try:
                if geom['type'] == 'Polygon':
                    coords = geom['coordinates'][0]
                else: # MultiPolygon
                    coords = geom['coordinates'][0][0]
                
                lon_c = sum(c[0] for c in coords) / len(coords)
                lat_c = sum(c[1] for c in coords) / len(coords)
                
                secciones_list.append({'Secc': s_id, 'lat': lat_c, 'lon': lon_c})
            except:
                continue
        
        df_centros_secc = pd.DataFrame(secciones_list)

        #3.3.3 Filtrar el DataFrame de secciones para este municipio
        df_secc_muni = df_secc[df_secc['Cve Mpio'] == st.session_state.muni_id].copy()

        #3.3.4 Crear mapa de secciones
        fig_secc = px.choropleth(
            df_secc_muni, 
            geojson=secciones_geojson_filtrado, 
            locations="Secc", # COLUMNAS EN EL CVS DE SECCION
            featureidkey="properties.SECCION", # Clave en tu JSON de secciones
            color="PRIO", # Pintar según prioridad
            color_discrete_map={'SI': '#FF8C00', 'NO': '#2E8B57'},
            projection="mercator"
        )
        
        
        # 3.3.5 NUMEROS BLANCO
        if not df_centros_secc.empty:
            fig_secc.add_scattergeo(
                lon = df_centros_secc['lon'],
                lat = df_centros_secc['lat'],
                text = df_centros_secc['Secc'],
                mode = 'text',
                textfont = dict(size=8, color="white", family="Arial Black"),
                hoverinfo='skip',
                showlegend=False
            )
        
        fig_secc.update_geos(fitbounds="locations", visible=False)
        fig_secc.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=500, showlegend=False)
        st.plotly_chart(fig_secc, use_container_width=True)

    with col_tabla:
        st.markdown(f"### 📋 Secciones")
        secciones_filtro = df_secc[df_secc['Cve Mpio'] == st.session_state.muni_id].copy()

        if not secciones_filtro.empty:
            def style_prio(df):
                color_map = pd.DataFrame('', index=df.index, columns=df.columns)
                mask = df['PRIO'] == 'SI'
                color_map.loc[mask, :] = 'background-color: #FF8C00; color: white; font-weight: bold;'
                return color_map

            st.dataframe(
                secciones_filtro.style.apply(style_prio, axis=None),
                column_order=("Secc", "Listado Nominal Total"),
                use_container_width=True,
                hide_index=True,
                height=450
            )
        else:
            st.warning("No hay datos de secciones.")

else:
    #3.4 VISTA GENERAL DEL MAPA
    st.info("Seleccione un municipio en el mapa para ver el desglose.")
    ids_todos = []
    nombres_todos = []
    for f in geojson_mun['features']:
        ids_todos.append(str(f['properties']['MUNICIPIO']))
        nombres_todos.append(f['properties']['NOMBRE'])
    
    df_base = pd.DataFrame({'ID': ids_todos, 'NOMBRE': nombres_todos})
    df_base['Color_Status'] = df_base['ID'].apply(lambda x: 'Prioritario' if x in municipios_naranja else 'Normal')

    fig_gral = px.choropleth(
        df_base, geojson=geojson_mun, locations="ID",
        featureidkey="properties.MUNICIPIO", color="Color_Status",
        hover_name="NOMBRE",
        color_discrete_map={'Prioritario': '#FF8C00', 'Normal': '#2E8B57'},
        projection="mercator"
    )

    fig_gral.update_traces(hoverlabel=dict(bgcolor="gray"), selector=dict(type='choropleth'))
    fig_gral.update_layout(hovermode="closest", clickmode="event+select")
    fig_gral.update_geos(fitbounds="locations", visible=False)
    fig_gral.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=600, showlegend=False)
    
    event = st.plotly_chart(fig_gral, on_select="rerun", use_container_width=True)
    
    if event and "selection" in event and event["selection"]["points"]:
        id_tocado = str(event["selection"]["points"][0]["location"])
        if id_tocado in municipios_naranja:
            st.session_state.muni_id = id_tocado
            st.rerun()
        else:
            st.toast(f"El municipio seleccionado no es prioritario.", icon="🚫")