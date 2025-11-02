import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import json
from datetime import datetime, timedelta
import numpy as np
import altair as alt

# --- Page Configuration ---
st.set_page_config(
    page_title="Building Health Dashboard",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Constants ---
CURRENT_YEAR = datetime.now().year
MIN_RESERVE_PER_FLAT_PER_YEAR = 500  # Example constant for reserve calculation

# --- Data Loading Functions with Caching ---
@st.cache_data
def load_data(file_path):
    """Loads CSV data with error handling."""
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"Error: {file_path} not found. Please make sure all data files are in the same directory.")
        return pd.DataFrame()

@st.cache_data
def load_json(file_path):
    """Loads JSON data with error handling."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Error: {file_path} not found. Please make sure all data files are in the same directory.")
        return None
    except json.JSONDecodeError:
        st.error(f"Error: Could not decode {file_path}. Please check the JSON format.")
        return None

# --- Health Calculation Functions ---

def calculate_financial_health(building, transactions_df, residents_df):
    """Calculates the financial health score for a single building."""
    if building.empty:
        return 0, {}

    # 1. Collection Rate
    collection_rate = (building['monthly_maintenance_collected'] / building['monthly_maintenance_expected']) * 100
    
    # 2. Reserve Ratio
    age = CURRENT_YEAR - building['year_built']
    required_reserve = building['total_flats'] * MIN_RESERVE_PER_FLAT_PER_YEAR * max(1, age)
    total_funds = building['current_fund'] + building['reserve_fund']
    reserve_ratio = total_funds / required_reserve if required_reserve > 0 else 1.0
    reserve_ratio_score = min(100, (reserve_ratio * 100)) # Cap at 100

    # 3. Payment Punctuality
    building_residents = residents_df[residents_df['building_id'] == building['building_id']]
    if not building_residents.empty:
        flats_with_no_dues = building_residents[building_residents['maintenance_due_amount'] == 0].shape[0]
        payment_punctuality = (flats_with_no_dues / building['total_flats']) * 100
    else:
        payment_punctuality = 0

    # 4. Expense Distribution (for detailed view)
    building_expenses = transactions_df[
        (transactions_df['building_id'] == building['building_id']) &
        (transactions_df['transaction_type'] == 'Expense')
    ]
    expense_dist = building_expenses.groupby('category')['amount'].sum().reset_index()

    # Final Score (Weighted Average)
    financial_score = (collection_rate * 0.4) + (reserve_ratio_score * 0.4) + (payment_punctuality * 0.2)
    
    details = {
        "Collection Rate (%)": collection_rate,
        "Total Funds (₹)": total_funds,
        "Required Reserve (₹)": required_reserve,
        "Reserve Ratio": reserve_ratio,
        "Payment Punctuality (%)": payment_punctuality,
        "Expense Distribution": expense_dist
    }
    
    return max(0, min(100, financial_score)), details

def calculate_structural_health(building, repairs_df):
    """Calculates the structural health score for a single building."""
    if building.empty:
        return 0, {}

    # 1. Age Score
    age = CURRENT_YEAR - building['year_built']
    age_score = max(0, 100 - (age * 1.5)) # Penalize older buildings

    # 2. Structural Audit Rating Score
    rating_map = {'A': 100, 'B': 80, 'C': 50, 'D': 20, 'F': 0}
    audit_rating_score = rating_map.get(building['structural_audit_rating'], 0)

    # 3. Repairs Score
    building_repairs = repairs_df[repairs_df['building_id'] == building['building_id']]
    num_open_issues = building_repairs[building_repairs['status'] == 'Open'].shape[0]
    num_high_severity = building_repairs[
        (building_repairs['status'] == 'Open') & 
        (building_repairs['severity'] == 'High')
    ].shape[0]
    
    # Penalize heavily for high severity issues
    repair_score = max(0, 100 - (num_open_issues * 5) - (num_high_severity * 20))

    # Final Score (Weighted Average)
    structural_score = (age_score * 0.2) + (audit_rating_score * 0.5) + (repair_score * 0.3)
    
    details = {
        "Building Age (Years)": age,
        "Audit Rating": building['structural_audit_rating'],
        "Open Issues": num_open_issues,
        "High Severity Issues": num_high_severity,
        "Repair Log": building_repairs
    }
    
    return max(0, min(100, structural_score)), details

def calculate_people_score(building, residents_df):
    """Calculates the 'Decency Index' / People Score."""
    if building.empty:
        return 0, {}
        
    building_residents = residents_df[residents_df['building_id'] == building['building_id']]
    if building_residents.empty:
        return 0, {}

    # 1. Payment Punctuality (re-calculated here for direct use)
    flats_with_no_dues = building_residents[building_residents['maintenance_due_amount'] == 0].shape[0]
    payment_punctuality = (flats_with_no_dues / building['total_flats']) * 100

    # 2. Ownership Ratio
    num_owners = building_residents[building_residents['owner_or_tenant'] == 'Owner'].shape[0]
    owner_ratio = (num_owners / building['total_flats']) * 100

    # 3. Socio-Economic Score (Mock)
    # Mapping income and education to scores
    income_map = { 'Low': 30, 'Medium': 70, 'High': 100 }
    edu_map = { 'High School': 50, 'Graduate': 80, 'Post-Graduate': 100 }
    
    building_residents['income_score'] = building_residents['avg_monthly_income'].map(income_map).fillna(0)
    building_residents['edu_score'] = building_residents['education_level'].map(edu_map).fillna(0)
    
    avg_income_score = building_residents['income_score'].mean()
    avg_edu_score = building_residents['edu_score'].mean()
    
    socio_economic_score = (avg_income_score * 0.6) + (avg_edu_score * 0.4)
    
    # Final Score (Weighted Average)
    # High weight on payment punctuality as per brief
    people_score = (payment_punctuality * 0.5) + (owner_ratio * 0.2) + (socio_economic_score * 0.3)
    
    details = {
        "Payment Punctuality (%)": payment_punctuality,
        "Owner-Tenant Ratio (%)": owner_ratio,
        "Avg. Income Score": avg_income_score,
        "Avg. Education Score": avg_edu_score,
        "Resident Details": building_residents
    }

    return max(0, min(100, people_score)), details

def check_nmmc_compliance(building, rules, financial_details):
    """Checks NMMC compliance rules from the JSON file."""
    if not rules:
        return 0, []

    pass_count = 0
    results = []
    today = datetime.now()
    
    for rule in rules['rules']:
        rule_id = rule['id']
        description = rule['description']
        condition_met = False
        details = ""

        try:
            if rule_id == "FIRE_SAFETY":
                last_inspection = pd.to_datetime(building['last_fire_safety'])
                condition_met = (today - last_inspection).days <= 365
                details = f"Last inspection: {last_inspection.date()}"
            
            elif rule_id == "STRUCT_AUDIT":
                last_inspection = pd.to_datetime(building['last_annual_inspection'])
                # Rule: Older buildings need more frequent checks
                age = CURRENT_YEAR - building['year_built']
                required_days = 365 if age > 15 else (365 * 3)
                days_since = (today - last_inspection).days
                condition_met = days_since <= required_days
                details = f"Last audit: {last_inspection.date()} ({days_since} days ago). Required every {required_days} days."

            elif rule_id == "RESERVE_FUND":
                reserve_ratio = financial_details.get("Reserve Ratio", 0)
                target = rule['parameters']['min_ratio']
                condition_met = reserve_ratio >= target
                details = f"Current Ratio: {reserve_ratio:.2f}, Target: {target}"
            
            elif rule_id == "WASTE_SEGREGATION":
                # This would typically be a boolean in the data, mocking it
                condition_met = building.get('waste_segregation_implemented', False)
                details = "Based on society records."
            
            elif rule_id == "SEWAGE_SYSTEM":
                # Mocking this as well
                condition_met = building.get('sewage_system_approved', False)
                details = "Based on NMMC approval records."

            if condition_met:
                pass_count += 1
                results.append({"Rule": description, "Status": "✅ Pass", "Details": details})
            else:
                results.append({"Rule": description, "Status": "❌ Fail", "Details": details})

        except Exception as e:
            results.append({"Rule": description, "Status": "⚠️ Error", "Details": f"Could not check rule: {e}"})

    compliance_score = (pass_count / len(rules['rules'])) * 100
    return compliance_score, results

def calculate_bhi(financial_score, structural_score, people_score):
    """Calculates the final Building Health Index (BHI)."""
    bhi = (financial_score * 0.5) + (structural_score * 0.3) + (people_score * 0.2)
    return max(0, min(100, bhi))

def get_bhi_color(bhi):
    """Returns a color based on the BHI score."""
    if bhi >= 80:
        return 'green'
    elif bhi >= 50:
        return 'orange'
    else:
        return 'red'

# --- Main Application ---
def main():
    # --- Sidebar ---
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
    
    # --- Load Data ---
    buildings_df = load_data("csv_data/sample_buildings.csv")
    residents_df = load_data("csv_data/sample_residents.csv")
    transactions_df = load_data("csv_data/transactions.csv")
    repairs_df = load_data("csv_data/repairs.csv")
    nmmc_rules = load_json("nmmc_rules.json")

    if buildings_df.empty or residents_df.empty or transactions_df.empty or repairs_df.empty or not nmmc_rules:
        st.error("One or more data files could not be loaded. The application cannot proceed.")
        return

    # --- Core Data Processing ---
    processed_data = []
    for _, building in buildings_df.iterrows():
        building_id = building['building_id']
        
        fin_score, fin_details = calculate_financial_health(building, transactions_df, residents_df)
        str_score, str_details = calculate_structural_health(building, repairs_df)
        ppl_score, ppl_details = calculate_people_score(building, residents_df)
        
        comp_score, comp_details = check_nmmc_compliance(building, nmmc_rules, fin_details)
        
        bhi_score = calculate_bhi(fin_score, str_score, ppl_score)
        
        processed_data.append({
            'building_id': building_id,
            'building_name': building['building_name'],
            'BHI': bhi_score,
            'Financial Score': fin_score,
            'Structural Score': str_score,
            'People Score': ppl_score,
            'Compliance Score': comp_score,
            'Latitude': building['latitude'],
            'Longitude': building['longitude'],
            'BHI Color': get_bhi_color(bhi_score),
            'fin_details': fin_details,
            'str_details': str_details,
            'ppl_details': ppl_details,
            'comp_details': comp_details
        })

    main_df = pd.DataFrame(processed_data)
    main_df = main_df.sort_values(by='BHI', ascending=False).reset_index(drop=True)

    # --- UI Tabs ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview & Ranking", 
        "🏢 Single Building Analysis", 
        "✅ NMMC Compliance Report", 
        "🗺️ Map View"
    ])

    # --- Tab 1: Overview & Ranking ---
    with tab1:
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
        bar_chart = alt.Chart(main_df).mark_bar().encode(
            x=alt.X('building_name', title="Building Name", sort='-y'),
            y=alt.Y('BHI', title="Building Health Index (BHI)"),
            color=alt.Color('BHI Color', scale=None), # Use pre-calculated color
            tooltip=['building_name', 'BHI']
        ).properties(
            title="Building Health Index (BHI) Ranking"
        ).interactive()
        
        st.altair_chart(bar_chart, use_container_width=True)

    # --- Tab 2: Single Building Analysis ---
    with tab2:
        st.header("Single Building Deep Dive")
        selected_building_name = st.selectbox(
            "Select a Building to Analyze",
            main_df['building_name']
        )
        
        if selected_building_name:
            data = main_df[main_df['building_name'] == selected_building_name].iloc[0]
            
            st.subheader(f"Analysis for: **{data['building_name']}**")
            
            # Top-level KPIs
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Building Health Index (BHI)", f"{data['BHI']:.1f}", 
                         help="Overall score (Finance: 50%, Structure: 30%, People: 20%)")
            col2.metric("Financial Score", f"{data['Financial Score']:.1f}")
            col3.metric("Structural Score", f"{data['Structural Score']:.1f}")
            col4.metric("People Score", f"{data['People Score']:.1f}")
            
            st.markdown("---")
            
            # Detailed Breakdown
            c1, c2 = st.columns(2)
            
            with c1:
                st.subheader("💰 Financial Details")
                st.metric("Total Funds", f"₹ {data['fin_details']['Total Funds']:,.0f}")
                st.metric("Required Reserve", f"₹ {data['fin_details']['Required Reserve']:,.0f}")
                
                fin_kpis = pd.DataFrame({
                    'Metric': ['Collection Rate', 'Reserve Ratio', 'Payment Punctuality'],
                    'Value': [
                        data['fin_details']['Collection Rate (%)'],
                        data['fin_details']['Reserve Ratio'],
                        data['fin_details']['Payment Punctuality (%)']
                    ],
                    'Unit': ['%', '', '%']
                })
                st.dataframe(fin_kpis.style.format({'Value': '{:.2f}'}), use_container_width=True)

                # Expense Pie Chart
                expense_df = data['fin_details']['Expense Distribution']
                if not expense_df.empty:
                    expense_chart = alt.Chart(expense_df).mark_arc(outerRadius=120).encode(
                        theta=alt.Theta("amount:Q", stack=True),
                        color=alt.Color("category:N", title="Category"),
                        tooltip=["category", "amount"]
                    ).properties(title="Expense Distribution")
                    st.altair_chart(expense_chart, use_container_width=True)
                else:
                    st.info("No expense data recorded for this building.")

            with c2:
                st.subheader("🧱 Structural Details")
                st.metric("Building Age", f"{data['str_details']['Building Age (Years)']} Years")
                st.metric("Structural Audit Rating", data['str_details']['Audit Rating'])
                st.metric("Open Repair Issues", data['str_details']['Open Issues'])
                st.metric("High Severity Issues", data['str_details']['High Severity Issues'], delta=data['str_details']['High Severity Issues'], delta_color="inverse")
                
                st.subheader("Open Repair Log")
                repair_log = data['str_details']['Repair Log']
                open_repairs = repair_log[repair_log['status'] == 'Open']
                if not open_repairs.empty:
                    st.dataframe(open_repairs[['issue_type', 'area', 'severity', 'estimated_cost']], use_container_width=True)
                else:
                    st.success("No open repair issues found.")
    
    # --- Tab 3: NMMC Compliance Report ---
    with tab3:
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

    # --- Tab 4: Map View ---
    with tab4:
        st.header("Navi Mumbai Building Health Map")
        st.markdown("Building locations color-coded by their BHI score: 🟢 **Healthy** (80+) 🟠 **Moderate** (50-79) 🔴 **Critical** (<50)")
        
        # Calculate center of map
        avg_lat = main_df['Latitude'].mean()
        avg_lon = main_df['Longitude'].mean()
        
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=13)

        for _, row in main_df.iterrows():
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

if __name__ == "__main__":
    main()
