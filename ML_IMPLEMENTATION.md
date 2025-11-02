# Machine Learning Implementation Guide

This document explains how Machine Learning (ML) has been integrated into the Building Health Dashboard using **Random Forest** algorithms.

## Overview

The ML implementation includes:
1. **Feature Engineering** - Creating meaningful features from raw data
2. **Risk Classification** - Random Forest Classifier to categorize buildings as Low/Medium/High risk
3. **BHI Prediction** - Random Forest Regressor to predict Building Health Index scores
4. **Feature Importance** - Identifying which factors most influence building health

## Architecture

### 1. Feature Engineering (`feature_engineering.py`)

**Purpose**: Transform raw data into ML-ready features

**Key Features Created**:
- **Building Characteristics**: Age, total flats, total residents
- **Financial Metrics**: Current fund, reserve fund, collection rate, reserve ratio
- **Structural Metrics**: Audit rating score, repair counts, repair costs
- **Resident Metrics**: Payment punctuality, owner ratio, average dues, socio-economic scores
- **Transaction Metrics**: Total expenses, total income, expense by category
- **Compliance Metrics**: Waste segregation, sewage approval status

**Function**:
```python
create_ml_features(buildings_df, residents_df, transactions_df, repairs_df)
```
Returns a DataFrame with engineered features for each building.

### 2. ML Models (`ml_models.py`)

#### A. Risk Classification (Random Forest Classifier)

**Purpose**: Classify buildings into risk categories (Low/Medium/High) based on BHI score thresholds

**Model Configuration**:
- Algorithm: Random Forest Classifier
- Estimators: 100 trees
- Max Depth: 10
- Random State: 42 (for reproducibility)

**Training Process**:
1. Split data: 80% training, 20% testing
2. Train Random Forest Classifier
3. Evaluate using accuracy and classification report
4. Save model for future use

**Outputs**:
- Trained classifier model
- Classification accuracy
- Classification report (precision, recall, F1-score)
- Confusion matrix

#### B. BHI Prediction (Random Forest Regressor)

**Purpose**: Predict continuous BHI scores (0-100) for buildings

**Model Configuration**:
- Algorithm: Random Forest Regressor
- Estimators: 100 trees
- Max Depth: 10
- Feature Scaling: StandardScaler

**Training Process**:
1. Scale features using StandardScaler
2. Split data: 80% training, 20% testing
3. Train Random Forest Regressor
4. Evaluate using MSE, R², and MAE
5. Save model and scaler for future use

**Outputs**:
- Trained regressor model
- Feature scaler
- Mean Squared Error (MSE)
- R² Score (coefficient of determination)
- Mean Absolute Error (MAE)

#### C. Feature Importance Analysis

**Purpose**: Identify which features most significantly influence building health

**Method**:
- Uses Random Forest's built-in feature importance
- Ranks features by their contribution to predictions
- Helps identify actionable factors

### 3. ML Insights View (`views/ml_insights.py`)

**Tabs**:

1. **Model Performance**
   - R² Score for regression
   - Mean Absolute Error
   - Mean Squared Error
   - Classification accuracy
   - Classification report

2. **Risk Predictions**
   - Actual vs Predicted risk categories
   - Risk distribution chart
   - Prediction accuracy

3. **Feature Importance**
   - Top 15 most important features
   - Visual bar chart
   - Detailed feature importance table

4. **BHI Predictions**
   - Actual vs Predicted BHI scores
   - Scatter plot with perfect prediction line
   - Error statistics

## How It Works

### Step 1: Feature Engineering
```python
features_df = create_ml_features(
    buildings_df, residents_df, transactions_df, repairs_df
)
```
Transforms raw data into numerical features suitable for ML.

### Step 2: Model Training
```python
ml_results = train_ml_models(features_df, bhi_scores)
```
- Creates risk categories from BHI scores (Low ≥80, Medium ≥50, High <50)
- Trains Random Forest Classifier for risk classification
- Trains Random Forest Regressor for BHI prediction
- Calculates feature importance

### Step 3: Predictions
```python
predicted_risk = predict_building_risk(building_features, classifier)
predicted_bhi = predict_building_bhi(building_features, regressor, scaler)
```
Uses trained models to make predictions on new or existing buildings.

## Integration into Main App

The ML functionality is integrated into `app.py`:

1. **After processing buildings**, ML features are created
2. **Models are trained** automatically when data is loaded
3. **New tab added**: "🤖 ML Insights & Predictions" 
4. **Results cached** for performance using Streamlit's `@st.cache_resource`

## Model Persistence

Trained models are saved to `ml_models/` directory:
- `risk_classifier.pkl` - Risk classification model
- `bhi_regressor.pkl` - BHI prediction model
- `scaler.pkl` - Feature scaler

Models can be reloaded using:
```python
models = load_saved_models()
```

## Benefits of Random Forest

1. **Handles Non-linear Relationships**: Captures complex patterns in data
2. **Feature Importance**: Automatically identifies important factors
3. **Robust**: Less prone to overfitting than single decision trees
4. **Handles Missing Values**: Can work with missing data
5. **No Feature Scaling Required (Classifier)**: Works with raw features
6. **Interpretable**: Feature importance provides insights

## Performance Metrics

### Classification Metrics
- **Accuracy**: Percentage of correct risk category predictions
- **Precision**: How many of the predicted positives are actually positive
- **Recall**: How many of the actual positives are predicted correctly
- **F1-Score**: Harmonic mean of precision and recall

### Regression Metrics
- **R² Score**: How well the model explains variance (0-1, higher is better)
- **MAE**: Average prediction error in BHI points
- **MSE**: Average squared prediction error

## Usage Examples

### Predicting Risk for a New Building
```python
# Prepare building features
features = create_ml_features(new_building_df, residents_df, ...)
building_features = features.iloc[0]

# Predict risk
predicted_risk = predict_building_risk(
    building_features, 
    ml_results['risk_classifier']
)
```

### Predicting BHI Score
```python
predicted_bhi = predict_building_bhi(
    building_features,
    ml_results['bhi_regressor'],
    ml_results['scaler']
)
```

## Future Enhancements

Potential improvements:
1. **Hyperparameter Tuning**: Use GridSearchCV to optimize model parameters
2. **Cross-Validation**: Implement k-fold cross-validation for better evaluation
3. **Time Series Prediction**: Predict future BHI trends based on historical data
4. **Anomaly Detection**: Identify unusual patterns in building data
5. **Ensemble Methods**: Combine multiple models for better predictions
6. **Deep Learning**: Add neural networks for more complex patterns
7. **Real-time Updates**: Retrain models as new data arrives

## Requirements

Additional dependencies for ML:
- `scikit-learn>=1.5.0` - Machine learning library
- `joblib>=1.3.0` - Model serialization

Install with:
```bash
pip install -r requirements.txt
```

## Troubleshooting

**Issue**: "ML models are not available"
- **Solution**: Ensure you have sufficient data (at least 2 buildings with valid features)

**Issue**: "Error training risk classifier"
- **Solution**: Check that you have buildings in different risk categories (Low, Medium, High)

**Issue**: Poor prediction accuracy
- **Solution**: 
  - Add more data for training
  - Review feature engineering
  - Try adjusting model hyperparameters
  - Check data quality

## Conclusion

The ML implementation provides powerful predictive capabilities using Random Forest algorithms. It enables:
- **Proactive risk management** through risk classification
- **BHI prediction** for new or existing buildings
- **Data-driven insights** through feature importance analysis
- **Performance monitoring** through comprehensive metrics

All ML functionality is seamlessly integrated into the dashboard and automatically trains when data is loaded.

