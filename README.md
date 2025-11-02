# Building Society Health Analysis Dashboard

A comprehensive **Streamlit-based dashboard** for analyzing and monitoring the health of residential building societies based on **NMMC (Navi Mumbai Municipal Corporation) guidelines**. The application evaluates buildings across multiple dimensions including financial health, structural integrity, resident quality, and regulatory compliance.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.51+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 📋 Table of Contents

- [Features](#-features)
- [Project Overview](#-project-overview)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Usage Guide](#-usage-guide)
- [Building Health Index (BHI)](#-building-health-index-bhi)
- [Machine Learning Implementation](#-machine-learning-implementation)
- [Data Format](#-data-format)
- [Configuration](#-configuration)
- [NMMC Compliance Rules](#-nmmc-compliance-rules)
- [API Documentation](#-api-documentation)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### 🏢 Core Functionality

- **Multi-Dimensional Health Analysis**
  - Financial Health Scoring (Collection Rate, Reserve Ratio, Payment Punctuality)
  - Structural Health Assessment (Age, Audit Ratings, Repair Issues)
  - People/Resident Quality Index (Payment Behavior, Ownership Ratio, Socio-Economic Factors)
  - NMMC Compliance Checking (Fire Safety, Structural Audits, Waste Management, Sewage Systems)

- **Building Health Index (BHI)**
  - Comprehensive scoring system (0-100 scale)
  - Weighted combination of Financial (50%), Structural (30%), and People (20%) scores
  - Color-coded visualization (Green: 80+, Orange: 50-79, Red: <50)

- **Interactive Dashboard**
  - Multi-building comparison and ranking
  - Individual building deep-dive analysis
  - Interactive maps with location-based visualization
  - Real-time data updates

### 🤖 Machine Learning Features

- **Random Forest Models**
  - Risk Classification (Low/Medium/High) based on BHI scores
  - BHI Prediction using regression models
  - Feature Importance Analysis to identify key health factors

- **ML Insights**
  - Model performance metrics (R², MAE, MSE, Accuracy)
  - Actual vs Predicted comparisons
  - Feature importance visualization
  - Risk prediction distribution

### ➕ Data Management

- **Form-Based Data Entry**
  - Add new buildings with comprehensive forms
  - Add residents to existing buildings
  - Add financial transactions (Income/Expense)
  - Auto-generated building IDs
  - Data validation and error handling

- **Data Persistence**
  - CSV-based data storage
  - Automatic data refresh
  - Cache management

### 📊 Visualizations

- **Interactive Charts**
  - BHI ranking bar charts (Altair)
  - Expense distribution pie charts
  - Compliance score comparisons
  - Feature importance analysis

- **Geographic Visualization**
  - Interactive Folium maps
  - Color-coded building markers
  - Location-based health insights

---

## 🎯 Project Overview

This dashboard provides a holistic view of building society health by combining:

1. **Financial Metrics**: Collection rates, reserve funds, payment punctuality
2. **Structural Metrics**: Building age, audit ratings, repair status
3. **Resident Metrics**: Payment behavior, ownership patterns, socio-economic indicators
4. **Compliance Metrics**: Adherence to NMMC regulations

The application helps:
- **Building Managers**: Monitor and improve building health
- **Residents**: Understand their building's status
- **Municipal Authorities**: Track compliance across buildings
- **Investors/Developers**: Assess building quality

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for cloning)

### Step-by-Step Installation

1. **Clone the repository** (or download and extract)
   ```bash
   git clone <repository-url>
   cd Building-Society-Health-Analysis-Dashboard-Under-NMMC-Guidelines-
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**
   ```bash
   streamlit --version
   python -c "import pandas, numpy, altair, folium, sklearn; print('All packages installed successfully!')"
   ```

### Dependencies

The project requires the following packages (see `requirements.txt`):

- **streamlit** (>=1.51.0): Web application framework
- **pandas** (>=2.3.3): Data manipulation and analysis
- **numpy** (>=2.3.4): Numerical computations
- **altair** (>=5.5.0): Statistical visualizations
- **folium** (>=0.20.0): Interactive maps
- **streamlit-folium** (>=0.25.3): Streamlit-Folium integration
- **scikit-learn** (>=1.5.0): Machine learning models
- **joblib** (>=1.3.0): Model serialization

---

## 🏃 Quick Start

1. **Start the application**
   ```bash
   streamlit run app.py
   ```

2. **Open in browser**
   - The application will automatically open at `http://localhost:8501`
   - If not, manually navigate to the URL shown in the terminal

3. **Explore the dashboard**
   - Navigate through different tabs
   - View building rankings and health scores
   - Check ML predictions and insights
   - Add new data using forms

---

## 📁 Project Structure

```
Building-Society-Health-Analysis-Dashboard-Under-NMMC-Guidelines/
│
├── app.py                      # Main Streamlit application entry point
├── config.py                   # Configuration constants and settings
├── data_loader.py              # CSV and JSON data loading functions
├── calculations.py             # Health score calculation functions
├── compliance.py               # NMMC compliance checking logic
├── feature_engineering.py     # ML feature engineering
├── ml_models.py               # Machine learning models (Random Forest)
├── utils.py                    # Utility functions (BHI calculation, colors)
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── ML_IMPLEMENTATION.md        # ML implementation details
├── MODULE_STRUCTURE.md         # Module structure documentation
│
├── csv_data/                   # Data files directory
│   ├── sample_buildings.csv    # Building master data
│   ├── sample_residents.csv   # Resident information
│   ├── transactions.csv        # Financial transactions
│   └── repairs.csv             # Repair and maintenance records
│
├── ml_models/                  # Trained ML models (auto-generated)
│   ├── risk_classifier.pkl     # Risk classification model
│   ├── bhi_regressor.pkl       # BHI prediction model
│   └── scaler.pkl              # Feature scaler
│
├── views/                      # UI component modules
│   ├── __init__.py
│   ├── overview.py             # Overview & Ranking tab
│   ├── building_detail.py      # Single Building Analysis tab
│   ├── compliance.py           # NMMC Compliance Report tab
│   ├── map_view.py             # Map View tab
│   ├── ml_insights.py          # ML Insights & Predictions tab
│   └── add_building.py         # Data entry forms
│
└── nmmc_rules.json            # NMMC compliance rules definition
```

---

## 📖 Usage Guide

### Dashboard Tabs

#### 1. 📊 Overview & Ranking
- **Multi-building comparison table** ranked by BHI
- **BHI bar chart** with color-coded health status
- Quick overview of all building health metrics

#### 2. 🏢 Single Building Analysis
- **Detailed breakdown** of individual building health
- **Financial details**: Collection rates, reserve ratios, expense distribution
- **Structural details**: Age, audit ratings, repair logs
- **Interactive charts** for expense categories

#### 3. ✅ NMMC Compliance Report
- **Compliance score comparison** across buildings
- **Detailed compliance checks** for individual buildings
- Rule-by-rule compliance status (Pass/Fail)

#### 4. 🗺️ Map View
- **Interactive map** showing all building locations
- **Color-coded markers** based on health status
- **Popup information** with key metrics

#### 5. 🤖 ML Insights & Predictions
- **Model Performance**: Metrics for regression and classification
- **Risk Predictions**: ML-based risk category predictions
- **Feature Importance**: Top factors affecting building health
- **BHI Predictions**: Actual vs Predicted BHI scores

#### 6. ➕ Add Data
- **Add Building**: Form to add new buildings
- **Add Resident**: Form to add residents to buildings
- **Add Transaction**: Form to add financial transactions

### Adding New Data

#### Adding a Building
1. Navigate to **➕ Add Data** tab → **🏢 Add Building**
2. Fill in building information:
   - Basic info (name, year built, flats, residents)
   - Financial data (funds, maintenance)
   - Structural data (audit rating, inspection dates)
   - Location (latitude, longitude)
   - Compliance status
3. Click **"Add Building"**
4. Click **"🔄 Refresh Data"** in sidebar to see changes

#### Adding a Resident
1. Navigate to **➕ Add Data** tab → **👥 Add Resident**
2. Select building from dropdown
3. Enter resident details (flat number, owner/tenant, income, education)
4. Enter payment information
5. Click **"Add Resident"**

#### Adding a Transaction
1. Navigate to **➕ Add Data** tab → **💰 Add Transaction**
2. Select building and enter transaction details
3. Choose transaction type (Income/Expense) and category
4. Enter amount and notes
5. Click **"Add Transaction"**

---

## 🏥 Building Health Index (BHI)

The Building Health Index (BHI) is a composite score (0-100) that measures overall building health.

### Calculation Formula

```
BHI = (Financial Score × 0.5) + (Structural Score × 0.3) + (People Score × 0.2)
```

### Component Scores

#### 1. Financial Health Score (50% weight)

**Sub-components:**
- **Collection Rate** (40%): `(Monthly Collected / Monthly Expected) × 100`
- **Reserve Ratio** (40%): `(Total Funds / Required Reserve) × 100`
- **Payment Punctuality** (20%): `(Flats with No Dues / Total Flats) × 100`

**Required Reserve Calculation:**
```
Required Reserve = Total Flats × ₹500 × max(1, Building Age)
```

#### 2. Structural Health Score (30% weight)

**Sub-components:**
- **Age Score** (20%): `max(0, 100 - (Age × 1.5))`
- **Audit Rating Score** (50%): A=100, B=80, C=50, D=20, F=0
- **Repair Score** (30%): `max(0, 100 - (Open Issues × 5) - (High Severity × 20))`

#### 3. People Score (20% weight)

**Sub-components:**
- **Payment Punctuality** (50%): Same as financial component
- **Owner Ratio** (20%): `(Owner Flats / Total Flats) × 100`
- **Socio-Economic Score** (30%): Weighted average of income and education scores

### Health Status Categories

- **🟢 Healthy (Green)**: BHI ≥ 80
- **🟠 Moderate (Orange)**: 50 ≤ BHI < 80
- **🔴 Critical (Red)**: BHI < 50

---

## 🤖 Machine Learning Implementation

### Models Used

1. **Random Forest Classifier**
   - Purpose: Classify buildings into risk categories (Low/Medium/High)
   - Features: 30+ engineered features from building, resident, and transaction data
   - Training: Automatic on data load

2. **Random Forest Regressor**
   - Purpose: Predict continuous BHI scores (0-100)
   - Features: Same as classifier
   - Scaling: StandardScaler for feature normalization

### Feature Engineering

The ML models use engineered features including:
- **Financial Features**: Collection rate, reserve ratio, funds, maintenance
- **Structural Features**: Age, audit rating, repair counts, repair costs
- **Resident Features**: Payment punctuality, owner ratio, average dues, socio-economic scores
- **Transaction Features**: Total expenses, total income, expense by category
- **Compliance Features**: Waste segregation, sewage approval

### Model Performance

Models are automatically evaluated using:
- **Classification**: Accuracy, Precision, Recall, F1-Score
- **Regression**: R² Score, Mean Absolute Error (MAE), Mean Squared Error (MSE)

### Feature Importance

The dashboard provides feature importance analysis showing which factors most significantly influence building health.

---

## 📊 Data Format

### Buildings Data (`sample_buildings.csv`)

| Column | Type | Description |
|--------|------|-------------|
| building_id | String | Unique building identifier (e.g., B001) |
| building_name | String | Name of the building |
| year_built | Integer | Year building was constructed |
| total_flats | Integer | Total number of flats |
| total_residents | Integer | Total number of residents |
| current_fund | Float | Current maintenance fund (₹) |
| reserve_fund | Float | Reserve fund amount (₹) |
| monthly_maintenance_collected | Float | Monthly maintenance collected (₹) |
| monthly_maintenance_expected | Float | Monthly maintenance expected (₹) |
| structural_audit_rating | String | Audit rating (A/B/C/D/F) |
| last_annual_inspection | Date | Last structural inspection date (YYYY-MM-DD) |
| last_fire_safety | Date | Last fire safety inspection date |
| latitude | Float | Building latitude coordinate |
| longitude | Float | Building longitude coordinate |
| waste_segregation_implemented | Boolean | Waste segregation status |
| sewage_system_approved | Boolean | Sewage system approval status |

### Residents Data (`sample_residents.csv`)

| Column | Type | Description |
|--------|------|-------------|
| building_id | String | Building identifier |
| flat_no | String | Flat/unit number |
| owner_or_tenant | String | Owner or Tenant |
| avg_monthly_income | String | Income category (Low/Medium/High) |
| education_level | String | Education level |
| num_occupants | Integer | Number of occupants |
| last_payment_date | Date | Last payment date |
| maintenance_due_amount | Float | Outstanding maintenance (₹) |

### Transactions Data (`transactions.csv`)

| Column | Type | Description |
|--------|------|-------------|
| building_id | String | Building identifier |
| date | Date | Transaction date |
| transaction_type | String | Income or Expense |
| category | String | Category (Maintenance, Security Salaries, Utilities, Repairs, Amenities) |
| amount | Float | Transaction amount (₹) |
| notes | String | Transaction notes |

### Repairs Data (`repairs.csv`)

| Column | Type | Description |
|--------|------|-------------|
| building_id | String | Building identifier |
| issue_id | String | Unique issue identifier |
| area | String | Affected area |
| issue_type | String | Type of issue |
| severity | String | Severity (Low/Medium/High) |
| status | String | Status (Open/Closed) |
| reported_date | Date | Issue report date |
| estimated_cost | Float | Estimated repair cost (₹) |

---

## ⚙️ Configuration

### Configuration File (`config.py`)

The configuration file contains all customizable constants:

#### Health Score Weights
```python
BHI_WEIGHTS = {
    'financial': 0.5,
    'structural': 0.3,
    'people': 0.2
}

FINANCIAL_WEIGHTS = {
    'collection_rate': 0.4,
    'reserve_ratio': 0.4,
    'payment_punctuality': 0.2
}
```

#### Financial Constants
```python
MIN_RESERVE_PER_FLAT_PER_YEAR = 500  # ₹ per flat per year
```

#### Risk Thresholds
```python
RISK_THRESHOLDS = {
    'Low': 80,
    'Medium': 50,
    'High': 0
}
```

#### ML Model Configuration
```python
ML_CONFIG = {
    'n_estimators': 100,
    'max_depth': 10,
    'random_state': 42,
    'test_size': 0.2
}
```

---

## ✅ NMMC Compliance Rules

The application checks compliance with the following NMMC rules (defined in `nmmc_rules.json`):

1. **FIRE_SAFETY**: Fire safety inspection within last 12 months
2. **STRUCT_AUDIT**: Structural audit (annual for buildings >15 years, every 3 years for <15 years)
3. **RESERVE_FUND**: Reserve fund ratio >= 1.0
4. **WASTE_SEGREGATION**: Waste segregation practices implemented
5. **SEWAGE_SYSTEM**: Sewage system NMMC approved and operational

### Customizing Rules

Edit `nmmc_rules.json` to add or modify compliance rules. Update `compliance.py` to add checking logic for new rules.

---

## 📚 API Documentation

### Main Modules

#### `data_loader.py`

- **`load_csv(file_path: str) -> pd.DataFrame`**
  - Loads CSV files with automatic boolean conversion
  - Handles errors gracefully
  
- **`load_json(file_path: str) -> dict`**
  - Loads JSON configuration files
  - Returns None on error

#### `calculations.py`

- **`calculate_financial_health(building, transactions_df, residents_df) -> tuple`**
  - Returns: `(financial_score, details_dict)`
  
- **`calculate_structural_health(building, repairs_df) -> tuple`**
  - Returns: `(structural_score, details_dict)`
  
- **`calculate_people_score(building, residents_df) -> tuple`**
  - Returns: `(people_score, details_dict)`

#### `compliance.py`

- **`check_nmmc_compliance(building, rules, financial_details) -> tuple`**
  - Returns: `(compliance_score, results_list)`

#### `ml_models.py`

- **`train_ml_models(features_df, bhi_scores) -> dict`**
  - Trains Random Forest models
  - Returns model results dictionary

- **`predict_building_risk(building_features, model, scaler) -> str`**
  - Predicts risk category (Low/Medium/High)

- **`predict_building_bhi(building_features, model, scaler) -> float`**
  - Predicts BHI score (0-100)

#### `utils.py`

- **`calculate_bhi(financial_score, structural_score, people_score) -> float`**
  - Calculates composite BHI score

- **`get_bhi_color(bhi: float) -> str`**
  - Returns color based on BHI ('green', 'orange', 'red')

---

## 🔧 Troubleshooting

### Common Issues

#### 1. **ModuleNotFoundError**
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

#### 2. **Data files not found**
```
Error: csv_data/sample_buildings.csv not found
```
- **Solution**: Ensure CSV files are in `csv_data/` directory
- Check file paths in `config.py`

#### 3. **ML model training errors**
```
Error: The least populated class in y has only 1 member
```
- **Solution**: Add more buildings with diverse BHI scores
- The app will use non-stratified split for small datasets

#### 4. **Port already in use**
```
Error: Port 8501 is already in use
```
- **Solution**: 
  ```bash
  streamlit run app.py --server.port 8502
  ```

#### 5. **Cache issues after adding data**
- **Solution**: Click "🔄 Refresh Data" button in sidebar
- Or restart the Streamlit app

### Performance Tips

1. **Large datasets**: Increase cache timeout in Streamlit config
2. **Slow ML training**: Reduce `n_estimators` in `ML_CONFIG`
3. **Memory issues**: Process buildings in batches

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Follow code style**: 
   - Use PEP 8 style guide
   - Add docstrings to functions
   - Include type hints
4. **Test your changes**: Ensure app runs without errors
5. **Commit changes**: `git commit -m 'Add amazing feature'`
6. **Push to branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Code Style

- Use meaningful variable names
- Add comments for complex logic
- Keep functions focused and small
- Write docstrings for all functions
- Follow the existing module structure

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **Streamlit** for the amazing web framework
- **NMMC** guidelines for compliance rules
- **scikit-learn** for machine learning capabilities
- **Altair** for beautiful visualizations
- **Folium** for interactive maps

---

## 📞 Support

For issues, questions, or suggestions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review [ML_IMPLEMENTATION.md](ML_IMPLEMENTATION.md) for ML details
3. Review [MODULE_STRUCTURE.md](MODULE_STRUCTURE.md) for architecture
4. Open an issue on GitHub

---

## 🔮 Future Enhancements

Potential improvements for future versions:

- [ ] Database integration (PostgreSQL, MongoDB)
- [ ] Real-time data updates via API
- [ ] Historical trend analysis
- [ ] Automated report generation (PDF)
- [ ] Email notifications for critical issues
- [ ] Multi-user authentication
- [ ] Advanced ML models (XGBoost, Neural Networks)
- [ ] Time series forecasting
- [ ] Mobile-responsive design
- [ ] Data export functionality (Excel, CSV)
- [ ] Building comparison tool
- [ ] Alert system for compliance violations

---

## 📊 Sample Screenshots

### Dashboard Overview
- Multi-building ranking table
- Color-coded health indicators
- Interactive charts

### ML Insights
- Model performance metrics
- Feature importance analysis
- Prediction comparisons

### Map View
- Interactive map with building locations
- Color-coded markers by health status
- Location-based insights

---

**Built with ❤️ using Streamlit and Python**

