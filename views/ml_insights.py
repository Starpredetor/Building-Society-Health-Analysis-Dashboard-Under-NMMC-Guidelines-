"""
ML Insights and Predictions tab view.
"""
import streamlit as st
import pandas as pd
import altair as alt
import numpy as np


def render_ml_insights_tab(main_df: pd.DataFrame, ml_results: dict):
    """
    Renders the ML Insights & Predictions tab.
    
    Args:
        main_df: DataFrame containing processed building data
        ml_results: Dictionary containing ML model results
    """
    st.header("🤖 Machine Learning Insights")
    st.markdown("""
    This section uses **Random Forest** algorithms to:
    - **Classify** buildings into risk categories (Low/Medium/High)
    - **Predict** Building Health Index (BHI) scores
    - **Identify** the most important factors affecting building health
    """)
    
    if not ml_results or ml_results.get('bhi_regressor') is None:
        st.warning("ML models are not trained yet. Please train models first.")
        return
    
    # Tab sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Model Performance",
        "🎯 Risk Predictions",
        "📈 Feature Importance",
        "🔮 BHI Predictions"
    ])
    
    with tab1:
        render_model_performance(ml_results)
    
    with tab2:
        render_risk_predictions(main_df, ml_results)
    
    with tab3:
        render_feature_importance(ml_results)
    
    with tab4:
        render_bhi_predictions(main_df, ml_results)


def render_model_performance(ml_results: dict):
    """Renders model performance metrics."""
    st.subheader("Model Performance Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    # Regression metrics
    if ml_results.get('r2_score') is not None:
        col1.metric("R² Score (BHI Prediction)", f"{ml_results['r2_score']:.3f}",
                   help="How well the model explains variance in BHI scores (1.0 = perfect)")
    
    if ml_results.get('mae') is not None:
        col2.metric("Mean Absolute Error", f"{ml_results['mae']:.2f}",
                   help="Average prediction error in BHI points")
    
    if ml_results.get('mse') is not None:
        col3.metric("Mean Squared Error", f"{ml_results['mse']:.2f}",
                   help="Average squared prediction error")
    
    # Classification metrics
    if ml_results.get('clf_accuracy') is not None:
        st.markdown("---")
        st.subheader("Risk Classification Performance")
        
        col1, col2 = st.columns(2)
        
        col1.metric("Classification Accuracy", f"{ml_results['clf_accuracy']:.1%}",
                   help="Percentage of correct risk category predictions")
        
        if ml_results.get('clf_report'):
            report_df = pd.DataFrame(ml_results['clf_report']).transpose()
            # Remove support row for display
            report_df = report_df.drop('support', errors='ignore')
            col2.dataframe(report_df, use_container_width=True)
    elif ml_results.get('risk_classifier') is None and ml_results.get('class_distribution'):
        st.markdown("---")
        st.subheader("Risk Classification Performance")
        st.info(
            f"Risk classifier not trained due to insufficient data.\n"
            f"Class distribution: {ml_results.get('class_distribution', {})}\n"
            f"For reliable classification, ensure at least 2 samples per risk category."
        )


def render_risk_predictions(main_df: pd.DataFrame, ml_results: dict):
    """Renders risk predictions for all buildings."""
    st.subheader("Risk Category Predictions")
    
    if ml_results.get('risk_classifier') is None:
        class_dist = ml_results.get('class_distribution', {})
        if class_dist:
            st.warning(
                f"Risk classifier not available due to insufficient data distribution.\n"
                f"Current class distribution: {class_dist}\n"
                f"To train a risk classifier, you need at least 2 samples per risk category."
            )
        else:
            st.info("Risk classifier not available. Models may need retraining with sufficient data.")
        
        # Show actual risk categories anyway
        if not main_df.empty:
            st.markdown("---")
            st.subheader("Actual Risk Categories (Based on BHI)")
            actual_risk = pd.DataFrame({
                'building_name': main_df['building_name'],
                'BHI': main_df['BHI'],
                'Risk Category': main_df['BHI'].apply(
                    lambda x: 'Low' if x >= 80 else ('Medium' if x >= 50 else 'High')
                )
            })
            st.dataframe(actual_risk, use_container_width=True)
        return
    
    # Get features for all buildings
    features_df = ml_results.get('features_df')
    if features_df is None or features_df.empty:
        st.warning("Feature data not available.")
        return
    
    # Predict risk for all buildings
    predictions = ml_results['risk_classifier'].predict(features_df)
    
    # Create predictions dataframe
    predictions_df = pd.DataFrame({
        'building_name': main_df['building_name'],
        'Actual BHI': main_df['BHI'],
        'Actual Risk': main_df['BHI'].apply(lambda x: 'Low' if x >= 80 else ('Medium' if x >= 50 else 'High')),
        'Predicted Risk': predictions,
        'Prediction Match': main_df['BHI'].apply(lambda x: 'Low' if x >= 80 else ('Medium' if x >= 50 else 'High')) == predictions
    })
    
    # Display predictions
    st.dataframe(predictions_df, use_container_width=True)
    
    # Risk distribution chart
    risk_counts = predictions_df['Predicted Risk'].value_counts()
    risk_chart = alt.Chart(pd.DataFrame({
        'Risk Category': risk_counts.index,
        'Count': risk_counts.values
    })).mark_bar().encode(
        x=alt.X('Risk Category', sort=['Low', 'Medium', 'High']),
        y='Count',
        color=alt.Color('Risk Category', scale=alt.Scale(
            domain=['Low', 'Medium', 'High'],
            range=['#28a745', '#ffc107', '#dc3545']
        ))
    ).properties(title="Predicted Risk Distribution")
    
    st.altair_chart(risk_chart, use_container_width=True)
    
    # Accuracy summary
    match_rate = predictions_df['Prediction Match'].mean()
    st.metric("Prediction Accuracy", f"{match_rate:.1%}")


def render_feature_importance(ml_results: dict):
    """Renders feature importance visualization."""
    st.subheader("Feature Importance Analysis")
    st.markdown("""
    This shows which factors most significantly influence building health according to the Random Forest model.
    """)
    
    feature_importance = ml_results.get('feature_importance')
    if feature_importance is None or feature_importance.empty:
        st.warning("Feature importance data not available.")
        return
    
    # Display top 15 features
    top_features = feature_importance.head(15)
    
    # Bar chart
    chart = alt.Chart(top_features).mark_bar().encode(
        x=alt.X('importance:Q', title='Importance'),
        y=alt.Y('feature:N', sort='-x', title='Feature'),
        color=alt.Color('importance:Q', scale=alt.Scale(scheme='viridis')),
        tooltip=['feature', 'importance']
    ).properties(
        title="Top 15 Most Important Features for Building Health",
        height=500
    )
    
    st.altair_chart(chart, use_container_width=True)
    
    # Table view
    st.subheader("Detailed Feature Importance")
    st.dataframe(feature_importance.style.format({'importance': '{:.4f}'}), use_container_width=True)


def render_bhi_predictions(main_df: pd.DataFrame, ml_results: dict):
    """Renders BHI prediction comparison."""
    st.subheader("BHI Score Predictions")
    st.markdown("Compare actual vs predicted BHI scores.")
    
    if ml_results.get('bhi_regressor') is None or ml_results.get('scaler') is None:
        st.info("BHI regressor not available. Models may need retraining.")
        return
    
    # Get features and predict
    features_df = ml_results.get('features_df')
    if features_df is None or features_df.empty:
        st.warning("Feature data not available.")
        return
    
    # Scale features
    features_scaled = ml_results['scaler'].transform(features_df)
    
    # Predict BHI
    predicted_bhi = ml_results['bhi_regressor'].predict(features_scaled)
    predicted_bhi = np.clip(predicted_bhi, 0, 100)  # Clamp to 0-100
    
    # Create comparison dataframe
    comparison_df = pd.DataFrame({
        'building_name': main_df['building_name'],
        'Actual BHI': main_df['BHI'],
        'Predicted BHI': predicted_bhi,
        'Difference': predicted_bhi - main_df['BHI'],
        'Absolute Error': np.abs(predicted_bhi - main_df['BHI'])
    })
    
    # Display comparison
    st.dataframe(comparison_df.style.format({
        'Actual BHI': '{:.1f}',
        'Predicted BHI': '{:.1f}',
        'Difference': '{:.1f}',
        'Absolute Error': '{:.1f}'
    }), use_container_width=True)
    
    # Scatter plot: Actual vs Predicted
    scatter_chart = alt.Chart(comparison_df).mark_circle(size=100).encode(
        x=alt.X('Actual BHI:Q', title='Actual BHI', scale=alt.Scale(domain=[0, 100])),
        y=alt.Y('Predicted BHI:Q', title='Predicted BHI', scale=alt.Scale(domain=[0, 100])),
        color=alt.Color('Absolute Error:Q', scale=alt.Scale(scheme='redyellowblue')),
        tooltip=['building_name', 'Actual BHI', 'Predicted BHI', 'Difference']
    ).properties(
        title="Actual vs Predicted BHI",
        width=500,
        height=500
    )
    
    # Add perfect prediction line
    perfect_line = pd.DataFrame({
        'Actual BHI': [0, 100],
        'Predicted BHI': [0, 100]
    })
    line_chart = alt.Chart(perfect_line).mark_line(color='red', strokeDash=[5, 5]).encode(
        x='Actual BHI:Q',
        y='Predicted BHI:Q'
    )
    
    st.altair_chart(scatter_chart + line_chart, use_container_width=True)
    
    # Summary statistics
    col1, col2, col3 = st.columns(3)
    col1.metric("Mean Absolute Error", f"{comparison_df['Absolute Error'].mean():.2f}")
    col2.metric("Max Error", f"{comparison_df['Absolute Error'].max():.2f}")
    col3.metric("Buildings within ±5 points", 
                f"{(comparison_df['Absolute Error'] <= 5).sum()}/{len(comparison_df)}")

