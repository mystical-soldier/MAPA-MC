import streamlit as st
import json
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="MAPA MC CHIAPAS 2026",
    page_icon="???",
    layout="wide"
)
# --- LISTA DE MUNICIPIOS A RESALTAR ---
municipios_naranja = ['102', '61', '90', '59','77','19','52','65','31','109','27','23','97','17','99','57','34','108','106','96','40','82']
# --- 1. CARGA DE DATOS ---
@st.cache_data
def load_data():
    #1.1 CARGA JSON
    #1.1.1 CARGA JSON MUNICIPIO
    with open("MUNICIPIO.json", encoding='utf-8') as f:
        geojson_mun = json.load(f)
    #1.1.2 CARGA JSON SECCION
    with open("SECCION.json", encoding='utf-8') as f:
        geojson_secc = json.load(f)      
    #1.1.3 CARGA JSON MANZANA    
    with open("MANZANA.json", encoding='utf-8') as f:
        geojson_manz = json.load(f)   
    #1.1.4 CARGA JSON LOCALIDAD    
    with open("LOCALIDAD.json", encoding='utf-8') as f:
        geojson_local = json.load(f)
    #1.1.5 CARGA JSON COLONIA
    with open("COLONIA.json", encoding='utf-8') as f:
        geojson_col = json.load(f)       
    #1.1.5 CARGA JSON CASILLA
    with open("CASILLA.json", encoding='utf-8') as f:
        geojson_casilla = json.load(f)
    #1.1.6 CARGA JSON PAVIMENTO
    with open("PAVIMENTO.json", encoding='utf-8') as f:
        geojson_pavimento = json.load(f)          
        
    #1.2 CARGA CSV - ORDEN (MUN-SECC-MANZ-CASILLA)
    #1.2.1 CSV DATOS MUNICIPIO
    df_muni = pd.read_csv("tu_archivo.csv", encoding='utf-8-sig', dtype={'MUNICIPIO': str})
    df_muni.columns = df_muni.columns.str.strip()
    #1.2.2 CSV TABLA SECCION
    df_secc = pd.read_csv("SECCION.csv", encoding='utf-8-sig', dtype={'Cve Mpio': str, 'Secc': str})
    df_secc.columns = df_secc.columns.str.strip()
    #1.2.3 CSV TABLA MANZANA
    df_manz = pd.read_csv("MANZANA.csv", encoding='utf-8-sig', dtype={'Secc': str, 'Manzana': str})
    df_manz.columns = df_manz.columns.str.strip()
    #1.2.4 CSV DATOS SECCION
    df_datmanz = pd.read_csv("INFO_MANZ.csv", encoding='utf-8-sig', dtype={'Secc': str})
    df_datmanz.columns = df_datmanz.columns.str.strip()
    
    return geojson_mun, geojson_secc, geojson_manz, geojson_local, geojson_col, geojson_casilla, geojson_pavimento, df_muni, df_secc, df_manz, df_datmanz

geojson_mun, geojson_secc, geojson_manz,geojson_local, geojson_col, geojson_casilla, geojson_pavimento, df_muni, df_secc, df_manz, df_datmanz = load_data()

# --- 2. ESTADO DE SELECCIoN ---
#CONDICIONALES
if 'muni_id' not in st.session_state:
    st.session_state.muni_id = None 
if 'seccion_id' not in st.session_state:
    st.session_state.seccion_id = None    

#---3. INTERFAZ ---
st.title("Analisis Estrategico Chiapas")
#----3.1  SECCION INTO MANZANA (Nivel mas profundo)
if st.session_state.muni_id and st.session_state.seccion_id:
    #---3.1 EXTRACCION DE INFORMACION DE LOS JSON
    #----3.1.1 EXTRAER INFO DE LOCALIDAD ---
    # Filtramos las localidades que pertenecen a la seccion seleccionada
    localidad_seccion = [
        c['properties'] for c in geojson_local['features'] 
        if str(c['properties'].get('SECCION')) == st.session_state.seccion_id
    ]
    #---3.1.2 EXTRAER INFO DE CASILLAS ---
    #----3.1.2.1Filtramos las casillas que pertenecen a la seccion seleccionada
    casillas_seccion = [
        c['properties'] for c in geojson_casilla['features'] 
        if str(c['properties'].get('seccion')) == st.session_state.seccion_id
    ]
    #---3.1.3 EXTRAER INFO PAVIMENTADA ---
    #----3.1.3.1 FILTRO QUE PERTENECE A LA CALLES PAVIMENTADAS DE LA SECCION
    pavimento_seccion = [
        d for d in geojson_pavimento['features'] 
        if str(d['properties'].get('SECCION')) == st.session_state.seccion_id
    ]
    #---3.1.4 EXTRAER INFO COLONIA ---
    #----3.1.4.1 FILTRO QUE PERTENECE A LAS COLONIAS DE LA SECCION
    colonias_seccion = [
        f for f in geojson_col['features'] 
        if str(f['properties'].get('seccion')) == st.session_state.seccion_id or
           str(f['properties'].get('SECCION')) == st.session_state.seccion_id
    ] 
     
    #---3.1.4 EXTRAER INFO DE MANZANAS
    #----3.1.4.1 FILTRADO INFORMACION DE MANZANAS
    df_manz_secc = df_manz[df_manz['Secc'] == st.session_state.seccion_id]   
    #----3.1.5.2 FILTRADO DATO GENERAL SECCION
    df_datmanz_secc = df_datmanz[df_datmanz['Secc'] == st.session_state.seccion_id]
    #---3.1.6 EXTRAER INFO DE CASILLAS
    #----3.1.6.1 EXTRAER DATOS JSON CASILLA
    info_geo_casilla = casillas_seccion[0] if casillas_seccion else {}
    # Extraemos la fila de la seccion actual del CSV de secciones
    # AsegUrate de que el nombre de la columna sea 'Secc' o como lo tengas en tu CSV
    datos_seccion_actual = df_secc[df_secc['Secc'] == st.session_state.seccion_id].iloc[0]
    
    #---3.1.5 BOTON DE REGRESO AL MAPA DEL MUNICIPIO  
    if st.button(f" REGRESAR A MAPA MUNICIPAL (SECC: {st.session_state.seccion_id})"):
        st.session_state.seccion_id = None
        st.rerun()
    #---3.1.7 CUADROS INFORMATIVOS NIVEL SECCION ---
    c1, c2, c3, c4, c5 = st.columns(5)
    #----3.1.7.1 RECUADRO DE INFORMACION 1 (MUNICIPIO Y SECCION)
    with c1:
        with st.container(border=True):
            st.subheader("UBICACION")
            st.write(f"Seccion: **{st.session_state.seccion_id}**")
            st.write(f"Municipio ID: **{st.session_state.muni_id}**")
    #----3.1.7.2 RECUADRO DE INFORMACION 2 UBICACION CASILLA (INFORMACION EXTRAIDA DEL JSON DE CASILLAS)        
    with c2:
        with st.container(border=True):
            st.subheader("DATOS DE CASILLA")
            if info_geo_casilla:
                st.write(f"**Domicilio:** {info_geo_casilla.get('domicilio', 'Sin dato')}")
                st.write(f"**Ubicacion:** {info_geo_casilla.get('ubicacion', 'Sin dato')}")
                st.info(f"**Ref:** {info_geo_casilla.get('referencia', 'Sin dato')}")
            else:
                st.warning("No hay datos de casilla para esta seccion.")
    with c3:
        with st.container(border=True):
            st.subheader("LOCALIDADES")
            # Supongamos que tienes una columna 'Localidad' en tu CSV de manzanas
            n_loc = df_manz_secc['Localidad'].nunique() if 'Localidad' in df_datmanz_secc.columns else "N/A"
            n_col = df_manz_secc['Colonia'].nunique() if 'Colonia' in df_datmanz_secc.columns else "N/A"
            st.write(f"Dentro de la seccion hay **{n_loc}** localidades y ademas cuenta con ***{n_col}*** colonias")
    with c4:
        with st.container(border=True): 
            st.subheader("LISTADO NOMINAL SECCIONAL")
            # Usamos el nombre de la columna exacto de tu CSV de SECCION
            ln_total = datos_seccion_actual['Listado Nominal Total']           
            # TambiEn puedes traer la participaciOn si esTA en ese CSV
            part_pje = datos_seccion_actual.get('PORCENTAJE PARTICIPACION CIUDADANA', 'N/A')
            st.write(f"LISTADO NOMINAL SECCIONAL: **{ln_total:,}**")
            st.write(f"PARTICIPACION ELECTORAL: **{part_pje}%**")
    with c5:
        with st.container(border=True):
            st.subheader(f"🏙️ Información de Colonias")
            if colonias_seccion:
                #Extraemos solo las propiedades (campos de texto) de cada colonia encontrada
                datos_tabla = [f['properties'] for f in colonias_seccion]
                #Convertimos a un DataFrame de Pandas para que se vea como tabla
                df_colonias = pd.DataFrame(datos_tabla)
                # Mostramos la tabla en Streamlit
                st.table(df_colonias)(
                    df_colonias, 
                    use_container_width=True, 
                    hide_index=True
                )
            else:
                st.info("No se encontraron registros de colonias para esta sección específica.")
            
    #---3.1.8 MAPA DE MANZANAS ---
    st.markdown(f"### Mapa de Manzanas - Seccion {st.session_state.seccion_id}")
    
    #----3.1.8.1 Filtrar GeoJSON por la seccion seleccionada
    manzanas_geo = {
        "type": "FeatureCollection",
        "features": [f for f in geojson_manz['features'] if str(f['properties'].get('SECCION')) == st.session_state.seccion_id]
    }   
    #----3.1.8.2 Calcular centros de cada manzana
    manza_list = []
    for f in manzanas_geo['features']:
        m_id = str(f['properties'].get('MANZANA'))
        geom = f['geometry'] # Cambiado geon por geom para consistencia
        
        try:
            if geom['type'] == 'Polygon':
                coords = geom['coordinates'][0]
            else: # MultiPolygon
                coords = geom['coordinates'][0][0]
            
            lon_m = sum(c[0] for c in coords) / len(coords)
            lat_m = sum(c[1] for c in coords) / len(coords)
            
            manza_list.append({'Manzana': m_id, 'lat': lat_m, 'lon': lon_m})
        except:
            continue  
            
    df_centros_manz = pd.DataFrame(manza_list)
        
    #----3.1.8.3 DIBUJAR EL MAPA DE LAS MANZANAS
    fig_manz = px.choropleth(
        df_manz_secc, 
        geojson=manzanas_geo, 
        locations="Manzana",
        featureidkey="properties.MANZANA", 
        color="PRIO",
        color_discrete_map={'SI': '#FF8C00', 'NO': '#2E8B57'},
        projection="mercator"
    )
    
    #---3.1.8.4 CAPA DE DELIMITACION DE LA SECCION (BORDE NEGRO) ---
    # Filtramos el GeoJSON de secciones para obtener solo la actual
    contorno_seccion = [
        f for f in geojson_secc['features'] 
        if str(f['properties'].get('SECCION')) == st.session_state.seccion_id or 
           str(f['properties'].get('seccion')) == st.session_state.seccion_id
    ]
    if contorno_seccion:
        #EXTRAEMOS LAS COORDENADAS DEL POLIGONO DE LA SECCION
        for feature in contorno_seccion:
            if feature['geometry']['type'] == 'Polygon':
                coords = feature['geometry']['coordinates'][0]
                lons = [c[0] for c in coords]
                lats = [c[1] for c in coords]
                
                fig_manz.add_scattergeo(
                    lat=lats,
                    lon=lons,
                    mode='lines',
                    line=dict(width=3, color='black'), # Borde negro grueso
                    hoverinfo='skip',
                    showlegend=False,
                    name="LIMITE DE SECCION"
                )
            elif feature['geometry']['type'] == 'MultiPolygon':
                for polygon in feature['geometry']['coordinates']:
                    coords = polygon[0]
                    lons = [c[0] for c in coords]
                    lats = [c[1] for c in coords]
                    
                    fig_manz.add_scattergeo(
                        lat=lats,
                        lon=lons,
                        mode='lines',
                        line=dict(width=3, color='black'),
                        hoverinfo='skip',
                        showlegend=False
                    )
    
    
    #----3.1.8.5 NuMEROS BLANCO (Alineado perfectamente con fig_manz)
    if not df_centros_manz.empty:
        fig_manz.add_scattergeo(
            lon = df_centros_manz['lon'],
            lat = df_centros_manz['lat'],
            text = df_centros_manz['Manzana'],
            mode = 'text',
            textfont = dict(size=8, color="white", family="Arial Black"),
            hoverinfo='skip',
            showlegend=False
        )
        
    #----3.1.8.6 CAPA COLONIAS      
    if geojson_col['features']:
    st.write("Campos encontrados en el JSON de Colonias:", geojson_col['features'][0]['properties'].keys())
    st.write("Valor de prueba en la primera colonia:", geojson_col['features'][0]['properties'])
        
    if colonias_seccion:
        for feature in colonias_seccion:
            geom_type = feature['geometry']['type']
            coords_list = []           
            # Manejo de Polígonos y MultiPolígonos
            if geom_type == 'Polygon':
                coords_list = [feature['geometry']['coordinates']]
            elif geom_type == 'MultiPolygon':
                coords_list = feature['geometry']['coordinates']
                
            for polygon in coords_list:
                #polygon[0] contiene los puntos del contorno exterior
                puntos = polygon[0]
                lons = [c[0] for c in puntos]
                lats = [c[1] for c in puntos]
                
                #Nombre de la colonia para el hover
                nombre_colonia = feature['properties'].get('NOMBRE', 'Colonia Sin Nombre')

                fig_manz.add_scattergeo(
                    lat=lats,
                    lon=lons,
                    mode='lines',
                    line=dict(
                        width=2, 
                        color='red' # Contorno rojo
                    ),
                    hovertext=f"Colonia: {nombre_colonia}",
                    hoverinfo='text',
                    showlegend=True,
                    name="Colonia"
                )    
        
    #----3.1.8.5 CAPA PAVIMENTO
    if pavimento_seccion:
        all_lats = []
        all_lons = []
        hover_textos = []
        for feature in pavimento_seccion:
            # Extraemos las coordenadas
            coords = feature['geometry']['coordinates']
            # IMPORTANTE: Validar si es LineString simple
            if feature['geometry']['type'] == 'LineString':
                # c[0] es Longitud, c[1] es Latitud
                lons = [c[0] for c in coords]
                lats = [c[1] for c in coords]
                all_lons.extend(lons + [None])
                all_lats.extend(lats + [None])

        # Usamos add_scattergeo con un color llamativo para probar (Rojo)
        #-----3.1.8.5.1 CAPA BASE (EL ASFALTO)
        fig_manz.add_scattergeo(
            lat=all_lats,
            lon=all_lons,
            mode='lines',
            line=dict(
                width=5,          # MAS ancha para que se vea como calle
                color='#333333'   # ASFALTO
            ),
            hovertext=hover_textos,
            hoverinfo='text',
            name="Pavimento"
        )
        #-----3.1.8.5.2 CAPA SUPERIOR (LA LINEA DIVISORIA)
        fig_manz.add_scattergeo(
            lat=all_lats,
            lon=all_lons,
            mode='lines',
            line=dict(
                width=1,          # Muy delgada
                color='white',    # Color de la raya central
                dash='dash'       # Esto la hace punteada (opcional)
            ),
            hoverinfo='skip',     # Para que no estorbe al pasar el mouse
            showlegend=False      # No queremos que aparezca dos veces en la leyenda
        )
    
    #----3.1.8.6 CAPA DE CASILLAS ---
    if casillas_seccion:
        df_casillas = pd.DataFrame(casillas_seccion)
        
        # Extraemos coordenadas manualmente del JSON original filtrado
        lats = [c['geometry']['coordinates'][1] for c in geojson_casilla['features'] if str(c['properties'].get('seccion')) == st.session_state.seccion_id]
        lons = [c['geometry']['coordinates'][0] for c in geojson_casilla['features'] if str(c['properties'].get('seccion')) == st.session_state.seccion_id]

        #CAPA DE VISUALIZACION EN EL MAPA
        fig_manz.add_scattergeo(
            lat=lats,
            lon=lons,
            mode='text',  # <--- IMPORTANTE: Solo texto para que se vea el emoji
            text='🗳️',    # <--- EMOJI URNA ELECTORAL
            textfont=dict(size=15), # TAMANO DE LETRA / EMOJI
            hovertext=[f"TIPO CASILLA: {c['casilla']}<br>UBICACION: {c['ubicacion']}" 
                for c in casillas_seccion
            ],
            hoverinfo='text',
            name="Casillas"
        )
    
    #----3.1.8.7 CAPA DE LOCALIDADES
    if localidad_seccion:
        df_localidad = pd.DataFrame(localidad_seccion)
        
        #-----3.1.8.6.1 Extraemos coordenadas manualmente del JSON original filtrado
        lats = [c['geometry']['coordinates'][1] for c in geojson_local['features'] if str(c['properties'].get('SECCION')) == st.session_state.seccion_id]
        lons = [c['geometry']['coordinates'][0] for c in geojson_local['features'] if str(c['properties'].get('SECCION')) == st.session_state.seccion_id]

        #-----3.1.8.7.1 Agregamos la capa
        fig_manz.add_scattergeo(
            lat=lats,
            lon=lons,
            mode ='text',
            text='📍',    # <--- EMOJI MARCADOR
            textfont=dict(size=15), # TAMANO DE LETRA / EMOJI
            hovertext=[f"NOMBRE: {c['NOMBRE']}<br>NUMERO: {c['LOCALIDAD']}" 
                for c in localidad_seccion
            ],
            hoverinfo='text',
            name="localidad" 
        )
     
    #----3.1.8.8 RENDERIZAR MAPA  
    fig_manz.update_geos(fitbounds="locations", visible=False)
    fig_manz.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=500)
    st.plotly_chart(fig_manz, use_container_width=True)    
     

#----3.2 CARGA DE MAPA DE MUNICIPIO
elif st.session_state.muni_id:
    
    info_muni = df_muni[df_muni['MUNICIPIO'] == st.session_state.muni_id].iloc[0]
    nombre_display = info_muni['NOMBRE MUNICIPIO']

    if st.button(f"Regresar (Viendo: {nombre_display})"):
        st.session_state.muni_id = None
        st.rerun()

    #3.2.1 --- FILA 1: CUADROS INFORMATIVOS ---
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        with st.container(border=True):
            st.subheader("INFORMACION MUNICIPAL")
            st.write(f"**{nombre_display}**. Distrito Federal: **{info_muni['DISTRITO FEDERAL']}**. Distrito Local: **{info_muni['DISTRITO LOCAL']}**.")
                                                                    
    with c2:
        with st.container(border=True):
            st.subheader("SECCIONES")
            st.write(f"Total: **{info_muni['SECCION']:,}**. Prioritarias: **{info_muni['SECCION PRIORITARIOS']:,}** ({info_muni['PORCENTAJE PRIORITARIO']}%).")
    
    with c3:
        with st.container(border=True):
            st.subheader("MANZANAS")
            st.write(f"Total: **{info_muni['MANZANA TOTAL']:,}**. SECCIONES PRIORITARIAS: **{info_muni['MANZANA PRIORITARIA']:,}**.")
    
    with c4:
        with st.container(border=True):
            st.subheader("PARTICIPACION")
            st.write(f"LISTADO NOMINAL.: **{info_muni['LISTADO NOMINAL']}**. PARTICIPACION CIUDADANA: **{info_muni['PORCENTAJE PARTICIPACION CIUDADANA']}**%.")

    #3.2.2 --- FILA 2: MAPA DE SECCIONES (CAMBIO AQUi) Y TABLA ---
    col_mapa, col_tabla = st.columns([1.8, 1.2])

    with col_mapa:
        st.markdown(f"###  Mapa Seccional de {nombre_display}")
        
       
        #3.2.2.1 FILTRO GeoJSON de secciones del municipio actual
        secciones_geojson_filtrado = {
            "type": "FeatureCollection",
            "features": [
                f for f in geojson_secc['features'] 
                if str(f['properties'].get('MUNICIPIO')) == st.session_state.muni_id
            ]
        }
        
        # 3.3.2 Calcular centros de cada seccion para poner el numero
        secciones_list = []
        for f in secciones_geojson_filtrado['features']:
            s_id = str(f['properties'].get('SECCION'))
            geom = f['geometry']
            
            #3.3.2.1 Logica para obtener el centro del poligono
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
            color="PRIO", # COLOR POR PRIORIDAD
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
        seleccion_secc = st.plotly_chart(fig_secc, on_select="rerun", use_container_width=True)

        # 2. La logica de deteccion debe estar pegada al mapa
        if seleccion_secc and "selection" in seleccion_secc and seleccion_secc["selection"]["points"]:
            secc_tocado = str(seleccion_secc["selection"]["points"][0]["location"])
            
            # Guardamos la seccion seleccionada
            st.session_state.seccion_id = secc_tocado
            st.rerun()

    with col_tabla:
        
        st.markdown(f"### Secciones")
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
    #3.2.3 VISTA GENERAL DEL MAPA
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

            st.toast(f"El municipio seleccionado no es prioritario.", icon="X")
