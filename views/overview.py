"""
Overview and Ranking tab view.
"""
import streamlit as st
import pandas as pd
import altair as alt


def render_overview_tab(main_df: pd.DataFrame):
    """
    Renders the Overview & Ranking tab.
    
    Args:
        main_df: DataFrame containing processed building data
    """
    st.header("Multi-Building Comparison & Ranking")
    st.markdown("This table ranks all buildings by their **Building Health Index (BHI)**.")
    
    st.dataframe(main_df[[
        'building_name', 'BHI', 'Financial Score', 'Structural Score', 'People Score', 'Compliance Score'
    ]].style.format({
        'BHI': '{:.1f}',
        'Financial Score': '{:.1f}',
        'Structural Score': '{:.1f}',
        'People Score': '{:.1f}',
        'Compliance Score': '{:.1f}'
    }), use_container_width=True)
    
    st.header("Overall Health Distribution")
    
    # BHI Bar Chart
    # Create a proper color scale mapping
    color_scale = alt.Scale(
        domain=['green', 'orange', 'red'],
        range=['#28a745', '#ffc107', '#dc3545']
    )
    bar_chart = alt.Chart(main_df).mark_bar().encode(
        x=alt.X('building_name', title="Building Name", sort='-y'),
        y=alt.Y('BHI', title="Building Health Index (BHI)"),
        color=alt.Color('BHI Color', scale=color_scale, legend=alt.Legend(title="Health Status")),
        tooltip=['building_name', 'BHI', 'Financial Score', 'Structural Score', 'People Score']
    ).properties(
        title="Building Health Index (BHI) Ranking"
    ).interactive()
    
    st.altair_chart(bar_chart, use_container_width=True)

