"""
Machine Learning models for Building Health Prediction and Classification.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    mean_squared_error, r2_score, mean_absolute_error
)
from sklearn.preprocessing import StandardScaler
import streamlit as st
import joblib
import os

# Model paths
MODEL_DIR = 'ml_models'
RISK_CLASSIFIER_PATH = os.path.join(MODEL_DIR, 'risk_classifier.pkl')
BHI_REGRESSOR_PATH = os.path.join(MODEL_DIR, 'bhi_regressor.pkl')
SCALER_PATH = os.path.join(MODEL_DIR, 'scaler.pkl')


def create_model_directory():
    """Creates directory for saving ML models."""
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)


def classify_risk_category(bhi: float) -> str:
    """
    Classifies building risk based on BHI score.
    
    Args:
        bhi: Building Health Index score (0-100)
        
    Returns:
        Risk category: 'Low', 'Medium', or 'High'
    """
    if bhi >= 80:
        return 'Low'
    elif bhi >= 50:
        return 'Medium'
    else:
        return 'High'


def prepare_ml_data(features_df: pd.DataFrame, bhi_scores: pd.Series) -> tuple:
    """
    Prepares data for machine learning.
    
    Args:
        features_df: DataFrame with engineered features
        bhi_scores: Series with BHI scores (target variable)
        
    Returns:
        Tuple of (X, y, feature_names)
    """
    # Select numeric features (exclude building_id)
    feature_columns = [col for col in features_df.columns if col != 'building_id']
    
    # Handle missing values
    X = features_df[feature_columns].fillna(0)
    
    # Get target variable (BHI)
    y = bhi_scores.fillna(0)
    
    return X, y, feature_columns


def train_risk_classifier(X: pd.DataFrame, y: pd.Series) -> tuple:
    """
    Trains a Random Forest Classifier for risk classification.
    
    Args:
        X: Feature matrix
        y: Target labels (risk categories)
        
    Returns:
        Tuple of (trained_model, accuracy, classification_report_dict)
    """
    # Check class distribution
    class_counts = y.value_counts()
    min_class_count = class_counts.min()
    
    # Determine if we can use stratified split (need at least 2 samples per class)
    use_stratify = min_class_count >= 2 and len(class_counts) >= 2
    
    if not use_stratify:
        # Check if we have enough data at all
        if len(X) < 4:  # Need at least 4 samples for train/test split
            raise ValueError(f"Insufficient data for training. Need at least 4 samples, got {len(X)}.")
        
        # Warn about class imbalance but proceed with non-stratified split
        if min_class_count < 2:
            import warnings
            warnings.warn(
                f"Class imbalance detected. Some classes have fewer than 2 samples: {class_counts.to_dict()}. "
                "Using non-stratified split. Consider collecting more data for better model performance."
            )
    
    # Split data (with or without stratification)
    if use_stratify:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
    
    # Train Random Forest Classifier
    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    clf.fit(X_train, y_train)
    
    # Predictions
    y_pred = clf.predict(X_test)
    
    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    confusion = confusion_matrix(y_test, y_pred)
    
    return clf, accuracy, report, confusion


def train_bhi_regressor(X: pd.DataFrame, y: pd.Series) -> tuple:
    """
    Trains a Random Forest Regressor for BHI prediction.
    
    Args:
        X: Feature matrix
        y: Target values (BHI scores)
        
    Returns:
        Tuple of (trained_model, mse, r2_score, mae)
    """
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest Regressor
    regressor = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    regressor.fit(X_train_scaled, y_train)
    
    # Predictions
    y_pred = regressor.predict(X_test_scaled)
    
    # Metrics
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    
    return regressor, scaler, mse, r2, mae


def get_feature_importance(model, feature_names: list) -> pd.DataFrame:
    """
    Gets feature importance from trained model.
    
    Args:
        model: Trained Random Forest model
        feature_names: List of feature names
        
    Returns:
        DataFrame with feature importance sorted by importance
    """
    importances = model.feature_importances_
    feature_importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': importances
    }).sort_values('importance', ascending=False)
    
    return feature_importance_df


@st.cache_resource
def train_ml_models(features_df: pd.DataFrame, bhi_scores: pd.Series) -> dict:
    """
    Trains all ML models and returns results.
    
    Args:
        features_df: DataFrame with engineered features
        bhi_scores: Series with BHI scores
        
    Returns:
        Dictionary containing trained models and metrics
    """
    create_model_directory()
    
    # Prepare data
    X, y_bhi, feature_names = prepare_ml_data(features_df, bhi_scores)
    
    # Create risk categories
    y_risk = pd.Series([classify_risk_category(bhi) for bhi in y_bhi], index=y_bhi.index)
    
    results = {
        'feature_names': feature_names,
        'features_df': X
    }
    
    # Train Risk Classifier
    # Check if we have enough data and classes for classification
    unique_classes = y_risk.unique()
    class_counts = y_risk.value_counts()
    
    if len(unique_classes) >= 2 and len(X) >= 4:
        # Check if all classes have at least 1 sample (for basic training)
        # But we'll handle the split differently based on minimum class count
        try:
            clf, clf_accuracy, clf_report, confusion = train_risk_classifier(X, y_risk)
            
            # Save classifier
            joblib.dump(clf, RISK_CLASSIFIER_PATH)
            
            results['risk_classifier'] = clf
            results['clf_accuracy'] = clf_accuracy
            results['clf_report'] = clf_report
            results['confusion_matrix'] = confusion
            results['risk_categories'] = y_risk
            results['class_distribution'] = class_counts.to_dict()
        except Exception as e:
            st.warning(
                f"Risk classifier training skipped: {str(e)}\n"
                f"Class distribution: {class_counts.to_dict()}\n"
                "The BHI regressor and feature importance will still be available."
            )
            results['risk_classifier'] = None
            results['class_distribution'] = class_counts.to_dict()
    else:
        if len(X) < 4:
            st.info(f"Insufficient data for risk classification. Need at least 4 samples, got {len(X)}.")
        elif len(unique_classes) < 2:
            st.info(f"Insufficient classes for risk classification. Found: {unique_classes.tolist()}")
        results['risk_classifier'] = None
        results['class_distribution'] = class_counts.to_dict() if len(class_counts) > 0 else {}
    
    # Train BHI Regressor
    try:
        regressor, scaler, mse, r2, mae = train_bhi_regressor(X, y_bhi)
        
        # Save regressor and scaler
        joblib.dump(regressor, BHI_REGRESSOR_PATH)
        joblib.dump(scaler, SCALER_PATH)
        
        results['bhi_regressor'] = regressor
        results['scaler'] = scaler
        results['mse'] = mse
        results['r2_score'] = r2
        results['mae'] = mae
    except Exception as e:
        st.warning(f"Error training BHI regressor: {str(e)}")
        results['bhi_regressor'] = None
    
    # Feature importance (from regressor if available, else classifier)
    if results.get('bhi_regressor'):
        results['feature_importance'] = get_feature_importance(
            results['bhi_regressor'], feature_names
        )
    elif results.get('risk_classifier'):
        results['feature_importance'] = get_feature_importance(
            results['risk_classifier'], feature_names
        )
    
    return results


def predict_building_risk(building_features: pd.Series, model, scaler=None) -> str:
    """
    Predicts risk category for a single building.
    
    Args:
        building_features: Series with building features
        model: Trained Random Forest Classifier
        scaler: Optional StandardScaler
        
    Returns:
        Predicted risk category
    """
    if model is None:
        return 'Unknown'
    
    # Prepare feature vector
    features = building_features.values.reshape(1, -1)
    
    # Scale if scaler provided
    if scaler:
        features = scaler.transform(features)
    
    # Predict
    prediction = model.predict(features)[0]
    return prediction


def predict_building_bhi(building_features: pd.Series, model, scaler) -> float:
    """
    Predicts BHI score for a single building.
    
    Args:
        building_features: Series with building features
        model: Trained Random Forest Regressor
        scaler: StandardScaler
        
    Returns:
        Predicted BHI score
    """
    if model is None or scaler is None:
        return 0.0
    
    # Prepare feature vector
    features = building_features.values.reshape(1, -1)
    
    # Scale
    features = scaler.transform(features)
    
    # Predict
    prediction = model.predict(features)[0]
    return max(0, min(100, prediction))  # Clamp between 0-100


def load_saved_models() -> dict:
    """
    Loads saved ML models from disk.
    
    Returns:
        Dictionary with loaded models
    """
    models = {}
    
    if os.path.exists(RISK_CLASSIFIER_PATH):
        models['risk_classifier'] = joblib.load(RISK_CLASSIFIER_PATH)
    
    if os.path.exists(BHI_REGRESSOR_PATH):
        models['bhi_regressor'] = joblib.load(BHI_REGRESSOR_PATH)
    
    if os.path.exists(SCALER_PATH):
        models['scaler'] = joblib.load(SCALER_PATH)
    
    return models

