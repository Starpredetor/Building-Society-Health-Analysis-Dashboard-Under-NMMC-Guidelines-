"""
NMMC Compliance Report tab view.
"""
import streamlit as st
import pandas as pd
import altair as alt


def render_compliance_tab(main_df: pd.DataFrame):
    """
    Renders the NMMC Compliance Report tab.
    
    Args:
        main_df: DataFrame containing processed building data
    """
    st.header("NMMC Compliance Report")
    st.markdown("Checks if buildings adhere to key NMMC regulations.")

    # Summary Chart
    comp_summary = main_df[['building_name', 'Compliance Score']]
    comp_chart = alt.Chart(comp_summary).mark_bar().encode(
        x=alt.X('building_name', title="Building Name", sort='-y'),
        y=alt.Y('Compliance Score', title="Compliance Score (%)"),
        tooltip=['building_name', 'Compliance Score']
    ).properties(
        title="Compliance Score by Building"
    ).interactive()
    st.altair_chart(comp_chart, use_container_width=True)
    
    st.markdown("---")
    
    # Detailed Report
    st.subheader("Detailed Compliance Check")
    compliance_building_name = st.selectbox(
        "Select a Building for Detailed Report",
        main_df['building_name'],
        key="compliance_select"
    )
    
    if compliance_building_name:
        data = main_df[main_df['building_name'] == compliance_building_name].iloc[0]
        st.dataframe(pd.DataFrame(data['comp_details']), use_container_width=True)

