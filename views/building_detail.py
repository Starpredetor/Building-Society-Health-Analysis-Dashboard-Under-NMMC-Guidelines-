"""
Single Building Analysis tab view.
"""
import streamlit as st
import pandas as pd
import altair as alt


def render_building_detail_tab(main_df: pd.DataFrame):
    """
    Renders the Single Building Analysis tab.
    
    Args:
        main_df: DataFrame containing processed building data
    """
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
            st.metric("Total Funds", f"₹ {data['fin_details']['Total Funds (₹)']:,.0f}")
            st.metric("Required Reserve", f"₹ {data['fin_details']['Required Reserve (₹)']:,.0f}")
            
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
            st.metric("High Severity Issues", data['str_details']['High Severity Issues'], 
                      delta=data['str_details']['High Severity Issues'], delta_color="inverse")
            
            st.subheader("Open Repair Log")
            repair_log = data['str_details']['Repair Log']
            open_repairs = repair_log[repair_log['status'] == 'Open']
            if not open_repairs.empty:
                st.dataframe(open_repairs[['issue_type', 'area', 'severity', 'estimated_cost']], 
                           use_container_width=True)
            else:
                st.success("No open repair issues found.")

