"""
Configuration constants for the Building Health Dashboard.
"""
from datetime import datetime

# Current year constant
CURRENT_YEAR = datetime.now().year

# Financial constants
MIN_RESERVE_PER_FLAT_PER_YEAR = 500  # Minimum reserve per flat per year in ₹

# Health score weights for BHI calculation
BHI_WEIGHTS = {
    'financial': 0.5,
    'structural': 0.3,
    'people': 0.2
}

# Financial health score weights
FINANCIAL_WEIGHTS = {
    'collection_rate': 0.4,
    'reserve_ratio': 0.4,
    'payment_punctuality': 0.2
}

# Structural health score weights
STRUCTURAL_WEIGHTS = {
    'age': 0.2,
    'audit_rating': 0.5,
    'repairs': 0.3
}

# People score weights
PEOPLE_WEIGHTS = {
    'payment_punctuality': 0.5,
    'owner_ratio': 0.2,
    'socio_economic': 0.3
}

# Socio-economic mapping
INCOME_SCORE_MAP = {'Low': 30, 'Medium': 70, 'High': 100}
EDUCATION_SCORE_MAP = {'High School': 50, 'Graduate': 80, 'Post-Graduate': 100}

# Structural audit rating mapping
AUDIT_RATING_MAP = {'A': 100, 'B': 80, 'C': 50, 'D': 20, 'F': 0}

# BHI color thresholds
BHI_COLOR_THRESHOLDS = {
    'green': 80,
    'orange': 50
}

# Data file paths
DATA_FILES = {
    'buildings': 'csv_data/sample_buildings.csv',
    'residents': 'csv_data/sample_residents.csv',
    'transactions': 'csv_data/transactions.csv',
    'repairs': 'csv_data/repairs.csv',
    'rules': 'nmmc_rules.json'
}

# Map default location (Navi Mumbai)
DEFAULT_MAP_CENTER = [19.0330, 73.0297]
DEFAULT_MAP_ZOOM = 13

# ML Model Configuration
ML_CONFIG = {
    'n_estimators': 100,
    'max_depth': 10,
    'random_state': 42,
    'test_size': 0.2
}

# Risk Category Thresholds
RISK_THRESHOLDS = {
    'Low': 80,
    'Medium': 50,
    'High': 0
}

