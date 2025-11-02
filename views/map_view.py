"""
Map View tab component.
"""
import streamlit as st
from streamlit_folium import st_folium
import folium
import pandas as pd
from config import DEFAULT_MAP_CENTER, DEFAULT_MAP_ZOOM


def render_map_tab(main_df: pd.DataFrame):
    """
    Renders the Map View tab.
    
    Args:
        main_df: DataFrame containing processed building data
    """
    st.header("Navi Mumbai Building Health Map")
    st.markdown("Building locations color-coded by their BHI score: 🟢 **Healthy** (80+) 🟠 **Moderate** (50-79) 🔴 **Critical** (<50)")
    
    # Calculate center of map (handle zero coordinates)
    valid_coords = main_df[(main_df['Latitude'] != 0) & (main_df['Longitude'] != 0)]
    if not valid_coords.empty:
        avg_lat = valid_coords['Latitude'].mean()
        avg_lon = valid_coords['Longitude'].mean()
    else:
        # Default to Navi Mumbai if no valid coordinates
        avg_lat, avg_lon = DEFAULT_MAP_CENTER
    
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=DEFAULT_MAP_ZOOM)

    for _, row in main_df.iterrows():
        # Skip buildings with invalid coordinates
        if row['Latitude'] == 0 or row['Longitude'] == 0:
            continue
            
        popup_html = f"""
        <b>{row['building_name']}</b><br>
        BHI: <b>{row['BHI']:.1f}</b><br>
        Finance: {row['Financial Score']:.1f}<br>
        Structure: {row['Structural Score']:.1f}<br>
        Compliance: {row['Compliance Score']:.1f}%
        """
        
        folium.Marker(
            [row['Latitude'], row['Longitude']],
            popup=folium.Popup(popup_html, max_width=200),
            tooltip=row['building_name'],
            icon=folium.Icon(color=row['BHI Color'])
        ).add_to(m)
        
    # Add legend
    legend_html = """
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 150px; height: 120px; 
                border:2px solid grey; z-index:9999; font-size:14px;
                background-color:white; opacity: 0.8;
                ">&nbsp; <b>BHI Legend</b><br>
                &nbsp; <i class="fa fa-map-marker fa-2x" style="color:green"></i>&nbsp; Healthy (80+)<br>
                &nbsp; <i class="fa fa-map-marker fa-2x" style="color:orange"></i>&nbsp; Moderate (50-79)<br>
                &nbsp; <i class="fa fa-map-marker fa-2x" style="color:red"></i>&nbsp; Critical (&lt;50)
    </div>
    """
    # Hack to add legend (st_folium doesn't natively support legends well)
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Display map
    st_folium(m, width='100%', height=600)

