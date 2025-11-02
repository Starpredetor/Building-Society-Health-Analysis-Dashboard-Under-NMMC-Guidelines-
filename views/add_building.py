"""
Add New Building form view.
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date
import os


def save_building_to_csv(building_data: dict, file_path: str):
    """
    Appends new building data to CSV file.
    
    Args:
        building_data: Dictionary with building data
        file_path: Path to CSV file
    """
    # Create DataFrame from building data
    new_row = pd.DataFrame([building_data])
    
    # Append to CSV
    if os.path.exists(file_path):
        # Read existing data
        existing_df = pd.read_csv(file_path)
        # Append new row
        updated_df = pd.concat([existing_df, new_row], ignore_index=True)
    else:
        updated_df = new_row
    
    # Save to CSV
    updated_df.to_csv(file_path, index=False)


def generate_building_id(existing_buildings_df: pd.DataFrame) -> str:
    """
    Generates a new building ID based on existing IDs.
    
    Args:
        existing_buildings_df: DataFrame with existing buildings
        
    Returns:
        New building ID (e.g., B009)
    """
    if existing_buildings_df.empty:
        return 'B001'
    
    # Extract numeric part from building IDs
    existing_ids = existing_buildings_df['building_id'].tolist()
    max_num = 0
    
    for bid in existing_ids:
        try:
            # Extract number from B001, B002, etc.
            num = int(bid[1:])
            max_num = max(max_num, num)
        except:
            continue
    
    # Generate new ID
    new_num = max_num + 1
    return f'B{new_num:03d}'


def render_add_building_tab(buildings_df: pd.DataFrame):
    """
    Renders the Add New Building form tab.
    
    Args:
        buildings_df: DataFrame with existing buildings data
    """
    st.header("➕ Add New Building")
    st.markdown("Fill out the form below to add a new building to the dashboard.")
    
    # Generate building ID
    new_building_id = generate_building_id(buildings_df)
    
    with st.form("add_building_form"):
        st.subheader("Building Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            building_id = st.text_input("Building ID", value=new_building_id, disabled=True,
                                       help="Auto-generated building ID")
            building_name = st.text_input("Building Name *", 
                                          placeholder="e.g., Greenfield Apartments",
                                          help="Name of the residential building")
            year_built = st.number_input("Year Built *", 
                                         min_value=1900, 
                                         max_value=datetime.now().year,
                                         value=2020,
                                         help="Year the building was constructed")
            total_flats = st.number_input("Total Flats *", 
                                         min_value=1, 
                                         max_value=1000,
                                         value=100,
                                         help="Total number of flats in the building")
            total_residents = st.number_input("Total Residents *", 
                                             min_value=1,
                                             value=300,
                                             help="Total number of residents")
        
        with col2:
            current_fund = st.number_input("Current Fund (₹) *", 
                                          min_value=0.0,
                                          value=1000000.0,
                                          format="%.2f",
                                          help="Current maintenance fund")
            reserve_fund = st.number_input("Reserve Fund (₹) *", 
                                           min_value=0.0,
                                           value=5000000.0,
                                           format="%.2f",
                                           help="Reserve fund amount")
            monthly_collected = st.number_input("Monthly Maintenance Collected (₹) *", 
                                                min_value=0.0,
                                                value=500000.0,
                                                format="%.2f",
                                                help="Monthly maintenance collected")
            monthly_expected = st.number_input("Monthly Maintenance Expected (₹) *", 
                                              min_value=0.0,
                                              value=600000.0,
                                              format="%.2f",
                                              help="Monthly maintenance expected")
        
        st.markdown("---")
        st.subheader("Structural & Compliance Information")
        
        col3, col4 = st.columns(2)
        
        with col3:
            structural_rating = st.selectbox(
                "Structural Audit Rating *",
                options=['A', 'B', 'C', 'D', 'F'],
                index=1,
                help="Latest structural audit rating (A = Best, F = Critical)"
            )
            
            last_annual_inspection = st.date_input(
                "Last Annual Inspection *",
                value=date(datetime.now().year, 1, 1),
                max_value=date.today(),
                help="Date of last annual structural inspection"
            )
            
            last_fire_safety = st.date_input(
                "Last Fire Safety Inspection *",
                value=date.today(),
                max_value=date.today(),
                help="Date of last fire safety inspection"
            )
        
        with col4:
            latitude = st.number_input(
                "Latitude *",
                min_value=-90.0,
                max_value=90.0,
                value=19.0330,
                format="%.6f",
                help="Building latitude coordinate"
            )
            
            longitude = st.number_input(
                "Longitude *",
                min_value=-180.0,
                max_value=180.0,
                value=73.0297,
                format="%.6f",
                help="Building longitude coordinate"
            )
            
            waste_segregation = st.checkbox(
                "Waste Segregation Implemented",
                value=True,
                help="Whether waste segregation is implemented"
            )
            
            sewage_approved = st.checkbox(
                "Sewage System Approved",
                value=True,
                help="Whether sewage system is NMMC approved"
            )
        
        st.markdown("---")
        
        # Submit button
        submitted = st.form_submit_button("Add Building", use_container_width=True, type="primary")
        
        if submitted:
            # Validate required fields
            if not building_name or building_name.strip() == "":
                st.error("⚠️ Building Name is required!")
                return
            
            if monthly_expected == 0:
                st.error("⚠️ Monthly Maintenance Expected must be greater than 0!")
                return
            
            # Check if building ID already exists
            if building_id in buildings_df['building_id'].values:
                st.error(f"⚠️ Building ID {building_id} already exists!")
                return
            
            # Prepare building data
            building_data = {
                'building_id': building_id,
                'building_name': building_name.strip(),
                'year_built': int(year_built),
                'total_flats': int(total_flats),
                'total_residents': int(total_residents),
                'current_fund': float(current_fund),
                'reserve_fund': float(reserve_fund),
                'monthly_maintenance_collected': float(monthly_collected),
                'monthly_maintenance_expected': float(monthly_expected),
                'structural_audit_rating': structural_rating,
                'last_annual_inspection': last_annual_inspection.strftime('%Y-%m-%d'),
                'last_fire_safety': last_fire_safety.strftime('%Y-%m-%d'),
                'latitude': float(latitude),
                'longitude': float(longitude),
                'waste_segregation_implemented': str(waste_segregation).lower(),
                'sewage_system_approved': str(sewage_approved).lower()
            }
            
            try:
                # Save to CSV
                buildings_file = 'csv_data/sample_buildings.csv'
                save_building_to_csv(building_data, buildings_file)
                
                st.success(f"✅ Building '{building_name}' (ID: {building_id}) added successfully!")
                st.info("🔄 Click 'Refresh Data' in the sidebar or restart the app to see the new building in the dashboard.")
                
                # Offer to refresh
                if st.button("🔄 Refresh Now", key="refresh_after_building"):
                    st.cache_data.clear()
                    st.cache_resource.clear()
                    st.rerun()
                
                # Show summary
                with st.expander("View Building Data", expanded=False):
                    st.json(building_data)
                    
            except Exception as e:
                st.error(f"❌ Error saving building data: {str(e)}")
                st.exception(e)


def render_add_resident_tab(buildings_df: pd.DataFrame):
    """
    Renders form to add residents for a building.
    
    Args:
        buildings_df: DataFrame with existing buildings
    """
    st.header("👥 Add Resident")
    st.markdown("Add resident information for an existing building.")
    
    if buildings_df.empty:
        st.warning("No buildings available. Please add a building first.")
        return
    
    with st.form("add_resident_form"):
        # Select building
        building_options = buildings_df.apply(
            lambda row: f"{row['building_id']} - {row['building_name']}", 
            axis=1
        ).tolist()
        
        selected_building = st.selectbox(
            "Select Building *",
            options=building_options,
            help="Choose the building for this resident"
        )
        
        building_id = selected_building.split(' - ')[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            flat_no = st.text_input("Flat Number *", 
                                   placeholder="e.g., A-101, 201",
                                   help="Flat or unit number")
            owner_or_tenant = st.selectbox(
                "Owner or Tenant *",
                options=['Owner', 'Tenant'],
                help="Residency type"
            )
            avg_monthly_income = st.selectbox(
                "Average Monthly Income *",
                options=['Low', 'Medium', 'High'],
                index=1,
                help="Income category"
            )
            education_level = st.selectbox(
                "Education Level *",
                options=['High School', 'Graduate', 'Post-Graduate'],
                index=1,
                help="Education qualification"
            )
        
        with col2:
            num_occupants = st.number_input(
                "Number of Occupants *",
                min_value=1,
                max_value=20,
                value=4,
                help="Number of people living in the flat"
            )
            last_payment_date = st.date_input(
                "Last Payment Date *",
                value=date.today(),
                max_value=date.today(),
                help="Date of last maintenance payment"
            )
            maintenance_due = st.number_input(
                "Maintenance Due Amount (₹) *",
                min_value=0.0,
                value=0.0,
                format="%.2f",
                help="Outstanding maintenance amount"
            )
        
        submitted = st.form_submit_button("Add Resident", use_container_width=True, type="primary")
        
        if submitted:
            if not flat_no or flat_no.strip() == "":
                st.error("⚠️ Flat Number is required!")
                return
            
            resident_data = {
                'building_id': building_id,
                'flat_no': flat_no.strip(),
                'owner_or_tenant': owner_or_tenant,
                'avg_monthly_income': avg_monthly_income,
                'education_level': education_level,
                'num_occupants': int(num_occupants),
                'last_payment_date': last_payment_date.strftime('%Y-%m-%d'),
                'maintenance_due_amount': float(maintenance_due)
            }
            
            try:
                residents_file = 'csv_data/sample_residents.csv'
                save_building_to_csv(resident_data, residents_file)
                
                st.success(f"✅ Resident added successfully for Building {building_id}!")
                st.info("🔄 Click 'Refresh Data' in the sidebar to see the updated data.")
                
                # Offer to refresh
                if st.button("🔄 Refresh Now", key="refresh_after_resident"):
                    st.cache_data.clear()
                    st.cache_resource.clear()
                    st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error saving resident data: {str(e)}")
                st.exception(e)


def render_add_transaction_tab(buildings_df: pd.DataFrame):
    """
    Renders form to add transactions for a building.
    
    Args:
        buildings_df: DataFrame with existing buildings
    """
    st.header("💰 Add Transaction")
    st.markdown("Add financial transactions (income or expense) for a building.")
    
    if buildings_df.empty:
        st.warning("No buildings available. Please add a building first.")
        return
    
    with st.form("add_transaction_form"):
        # Select building
        building_options = buildings_df.apply(
            lambda row: f"{row['building_id']} - {row['building_name']}", 
            axis=1
        ).tolist()
        
        selected_building = st.selectbox(
            "Select Building *",
            options=building_options,
            help="Choose the building for this transaction"
        )
        
        building_id = selected_building.split(' - ')[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            transaction_date = st.date_input(
                "Transaction Date *",
                value=date.today(),
                max_value=date.today(),
                help="Date of the transaction"
            )
            transaction_type = st.selectbox(
                "Transaction Type *",
                options=['Income', 'Expense'],
                help="Type of transaction"
            )
            category = st.selectbox(
                "Category *",
                options=['Maintenance', 'Security Salaries', 'Utilities', 'Repairs', 'Amenities'],
                help="Transaction category"
            )
        
        with col2:
            amount = st.number_input(
                "Amount (₹) *",
                min_value=0.01,
                value=10000.0,
                format="%.2f",
                help="Transaction amount"
            )
            notes = st.text_area(
                "Notes",
                placeholder="e.g., January salary payment, Monthly maintenance collection",
                help="Additional notes about the transaction"
            )
        
        submitted = st.form_submit_button("Add Transaction", use_container_width=True, type="primary")
        
        if submitted:
            transaction_data = {
                'building_id': building_id,
                'date': transaction_date.strftime('%Y-%m-%d'),
                'transaction_type': transaction_type,
                'category': category,
                'amount': float(amount),
                'notes': notes.strip() if notes else ""
            }
            
            try:
                transactions_file = 'csv_data/transactions.csv'
                save_building_to_csv(transaction_data, transactions_file)
                
                st.success(f"✅ Transaction added successfully for Building {building_id}!")
                st.info("🔄 Click 'Refresh Data' in the sidebar to see the updated data.")
                
                # Offer to refresh
                if st.button("🔄 Refresh Now", key="refresh_after_transaction"):
                    st.cache_data.clear()
                    st.cache_resource.clear()
                    st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error saving transaction data: {str(e)}")
                st.exception(e)

