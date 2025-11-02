"""
Building Health Dashboard - Main Application

This Streamlit application analyzes the health of residential societies
based on NMMC guidelines.
"""
import streamlit as st
import pandas as pd

from config import DATA_FILES
from data_loader import load_csv, load_json
from calculations import calculate_financial_health, calculate_structural_health, calculate_people_score
from compliance import check_nmmc_compliance
from utils import calculate_bhi, get_bhi_color
from feature_engineering import create_ml_features
from ml_models import train_ml_models
from views import (
    render_overview_tab,
    render_building_detail_tab,
    render_compliance_tab,
    render_map_tab,
    render_ml_insights_tab,
    render_add_building_tab,
    render_add_resident_tab,
    render_add_transaction_tab
)

# --- Page Configuration ---
st.set_page_config(
    page_title="Building Health Dashboard",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_all_data():
    """
    Loads all required data files.
    
    Returns:
        Tuple of (buildings_df, residents_df, transactions_df, repairs_df, nmmc_rules)
        Returns None values if any critical file fails to load
    """
    buildings_df = load_csv(DATA_FILES['buildings'])
    residents_df = load_csv(DATA_FILES['residents'])
    transactions_df = load_csv(DATA_FILES['transactions'])
    repairs_df = load_csv(DATA_FILES['repairs'])
    nmmc_rules = load_json(DATA_FILES['rules'])
    
    return buildings_df, residents_df, transactions_df, repairs_df, nmmc_rules


def process_buildings(buildings_df, residents_df, transactions_df, repairs_df, nmmc_rules):
    """
    Processes all buildings and calculates their health scores.
    
    Args:
        buildings_df: DataFrame with building data
        residents_df: DataFrame with resident data
        transactions_df: DataFrame with transaction data
        repairs_df: DataFrame with repair data
        nmmc_rules: Dictionary with NMMC compliance rules
        
    Returns:
        DataFrame with processed building data
    """
    processed_data = []
    
    for _, building in buildings_df.iterrows():
        try:
            building_id = building.get('building_id', '')
            if pd.isna(building_id) or building_id == '':
                st.warning(f"Skipping building with missing ID: {building.get('building_name', 'Unknown')}")
                continue
            
            # Calculate health scores
            fin_score, fin_details = calculate_financial_health(building, transactions_df, residents_df)
            str_score, str_details = calculate_structural_health(building, repairs_df)
            ppl_score, ppl_details = calculate_people_score(building, residents_df)
            
            # Check compliance
            comp_score, comp_details = check_nmmc_compliance(building, nmmc_rules, fin_details)
            
            # Calculate BHI
            bhi_score = calculate_bhi(fin_score, str_score, ppl_score)
            
            # Extract building metadata
            building_name = building.get('building_name', f'Building {building_id}')
            latitude = building.get('latitude', 0)
            longitude = building.get('longitude', 0)
            
            # Handle NaN values for coordinates
            if pd.isna(latitude):
                latitude = 0
            if pd.isna(longitude):
                longitude = 0
            
            # Store processed data
            processed_data.append({
                'building_id': building_id,
                'building_name': building_name,
                'BHI': bhi_score,
                'Financial Score': fin_score,
                'Structural Score': str_score,
                'People Score': ppl_score,
                'Compliance Score': comp_score,
                'Latitude': latitude,
                'Longitude': longitude,
                'BHI Color': get_bhi_color(bhi_score),
                'fin_details': fin_details,
                'str_details': str_details,
                'ppl_details': ppl_details,
                'comp_details': comp_details
            })
        except Exception as e:
            st.warning(f"Error processing building {building.get('building_name', 'Unknown')}: {str(e)}")
            continue
    
    # Create DataFrame and sort by BHI
    main_df = pd.DataFrame(processed_data)
    if not main_df.empty:
        main_df = main_df.sort_values(by='BHI', ascending=False).reset_index(drop=True)
    
    return main_df


def render_sidebar():
    """Renders the sidebar with app information."""
    st.sidebar.title("🏙️ Building Health Dashboard")
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    This app analyzes the health of residential societies based on NMMC guidelines.
    
    It evaluates buildings on:
    - **💰 Financial Health**
    - **🧱 Structural Health**
    - **😊 Resident (People) Analysis**
    - **✅ NMMC Compliance**
    """)
    st.sidebar.markdown("---")
    st.sidebar.info("Data is loaded from local CSV and JSON files.")
    
    # Add refresh button
    if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()


def main():
    """Main application function."""
    # Render sidebar
    render_sidebar()
    
    # Load data
    buildings_df, residents_df, transactions_df, repairs_df, nmmc_rules = load_all_data()
    
    # Validate data loading
    if (buildings_df.empty or residents_df.empty or transactions_df.empty or 
        repairs_df.empty or not nmmc_rules):
        st.error("One or more data files could not be loaded. The application cannot proceed.")
        return
    
    # Process buildings
    with st.spinner("Processing building data..."):
        main_df = process_buildings(
            buildings_df, residents_df, transactions_df, repairs_df, nmmc_rules
        )
    
    if main_df.empty:
        st.error("No buildings were successfully processed. Please check your data.")
        return
    
    # Prepare ML features and train models
    ml_results = None
    if not main_df.empty:
        with st.spinner("Preparing ML features and training models..."):
            try:
                # Create ML features
                features_df = create_ml_features(
                    buildings_df, residents_df, transactions_df, repairs_df
                )
                
                # Get BHI scores for training
                bhi_scores = main_df.set_index('building_id')['BHI']
                
                # Align features with BHI scores by building_id
                features_df = features_df.set_index('building_id')
                common_ids = features_df.index.intersection(bhi_scores.index)
                
                if len(common_ids) > 0:
                    features_df = features_df.loc[common_ids]
                    bhi_scores = bhi_scores.loc[common_ids]
                    
                    # Train ML models
                    ml_results = train_ml_models(features_df, bhi_scores)
                    ml_results['features_df'] = features_df  # Store for predictions
            except Exception as e:
                st.warning(f"ML model training encountered an issue: {str(e)}")
                ml_results = None
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Overview & Ranking", 
        "🏢 Single Building Analysis", 
        "✅ NMMC Compliance Report", 
        "🗺️ Map View",
        "🤖 ML Insights & Predictions",
        "➕ Add Data"
    ])
    
    # Render tabs
    with tab1:
        render_overview_tab(main_df)
    
    with tab2:
        render_building_detail_tab(main_df)
    
    with tab3:
        render_compliance_tab(main_df)
    
    with tab4:
        render_map_tab(main_df)
    
    with tab5:
        if ml_results:
            render_ml_insights_tab(main_df, ml_results)
        else:
            st.info("ML models are not available. Ensure you have sufficient data for training.")
    
    with tab6:
        # Sub-tabs for different data entry forms
        add_tab1, add_tab2, add_tab3 = st.tabs([
            "🏢 Add Building",
            "👥 Add Resident",
            "💰 Add Transaction"
        ])
        
        with add_tab1:
            render_add_building_tab(buildings_df)
        
        with add_tab2:
            render_add_resident_tab(buildings_df)
        
        with add_tab3:
            render_add_transaction_tab(buildings_df)


if __name__ == "__main__":
    main()
