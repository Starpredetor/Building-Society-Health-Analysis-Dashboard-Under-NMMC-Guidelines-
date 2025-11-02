# Building Health Dashboard - Module Structure

This document describes the modular structure of the Building Health Dashboard application.

## Project Structure

```
Building-Society-Health-Analysis-Dashboard-Under-NMMC-Guidelines/
│
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration constants
├── data_loader.py              # Data loading functions
├── calculations.py             # Health calculation functions
├── compliance.py               # NMMC compliance checking
├── utils.py                    # Utility functions
│
├── views/                      # UI components
│   ├── __init__.py
│   ├── overview.py            # Overview & Ranking tab
│   ├── building_detail.py     # Single Building Analysis tab
│   ├── compliance.py          # NMMC Compliance Report tab
│   └── map_view.py             # Map View tab
│
├── csv_data/                   # Data files
│   ├── sample_buildings.csv
│   ├── sample_residents.csv
│   ├── transactions.csv
│   └── repairs.csv
│
└── nmmc_rules.json            # NMMC compliance rules
```

## Module Descriptions

### 1. `config.py`
**Purpose**: Stores all configuration constants and settings.

**Contents**:
- Current year constant
- Financial constants (MIN_RESERVE_PER_FLAT_PER_YEAR)
- Health score weights for BHI calculation
- Financial, Structural, and People score weights
- Socio-economic mapping dictionaries
- Structural audit rating mapping
- BHI color thresholds
- Data file paths
- Map default location and zoom settings

**Benefits**:
- Centralized configuration management
- Easy to update constants
- No magic numbers in code

### 2. `data_loader.py`
**Purpose**: Handles all data loading operations with error handling.

**Functions**:
- `load_csv(file_path)`: Loads CSV files with automatic boolean conversion
- `load_json(file_path)`: Loads JSON files with error handling

**Features**:
- Streamlit caching for performance
- Automatic boolean type conversion
- Comprehensive error handling
- User-friendly error messages

### 3. `calculations.py`
**Purpose**: Contains all health calculation logic.

**Functions**:
- `calculate_financial_health()`: Calculates financial health score
- `calculate_structural_health()`: Calculates structural health score
- `calculate_people_score()`: Calculates people/resident score

**Features**:
- Separation of calculation logic from UI
- Easy to test individual functions
- Reusable across different contexts

### 4. `compliance.py`
**Purpose**: Handles NMMC compliance checking.

**Functions**:
- `check_nmmc_compliance()`: Checks all NMMC compliance rules

**Features**:
- Centralized compliance logic
- Easy to add new rules
- Clear rule-based structure

### 5. `utils.py`
**Purpose**: Utility functions used throughout the application.

**Functions**:
- `calculate_bhi()`: Calculates Building Health Index
- `get_bhi_color()`: Determines color based on BHI score

**Features**:
- Reusable utility functions
- Centralized helper logic

### 6. `views/` Directory
**Purpose**: Contains all UI components organized by tab.

**Modules**:
- `overview.py`: Renders Overview & Ranking tab
- `building_detail.py`: Renders Single Building Analysis tab
- `compliance.py`: Renders NMMC Compliance Report tab
- `map_view.py`: Renders Map View tab

**Benefits**:
- Separation of UI logic from business logic
- Easy to modify individual tabs
- Better code organization
- Easier to test UI components

### 7. `app.py`
**Purpose**: Main application entry point.

**Functions**:
- `main()`: Main application flow
- `load_all_data()`: Loads all data files
- `process_buildings()`: Processes all buildings and calculates scores
- `render_sidebar()`: Renders sidebar UI

**Features**:
- Clean, readable main application flow
- Clear separation of concerns
- Easy to understand application structure

## Benefits of This Structure

1. **Maintainability**: Each module has a clear, single responsibility
2. **Testability**: Individual modules can be tested independently
3. **Scalability**: Easy to add new features or modify existing ones
4. **Readability**: Code is organized logically and easy to navigate
5. **Reusability**: Functions can be reused across different contexts
6. **Collaboration**: Multiple developers can work on different modules simultaneously

## Adding New Features

### Adding a New Calculation
1. Add the calculation function to `calculations.py`
2. Import and use it in `app.py` or the relevant view

### Adding a New Tab
1. Create a new file in `views/` directory (e.g., `new_tab.py`)
2. Create a render function (e.g., `render_new_tab()`)
3. Export it in `views/__init__.py`
4. Add it to the tabs in `app.py`

### Adding a New Configuration
1. Add the constant to `config.py`
2. Import and use it in the relevant module

### Adding a New Compliance Rule
1. Add the rule to `nmmc_rules.json`
2. Add the checking logic to `compliance.py` in `check_nmmc_compliance()`

## Best Practices

1. **Keep functions focused**: Each function should do one thing well
2. **Use type hints**: Help with code documentation and IDE support
3. **Handle errors gracefully**: Provide user-friendly error messages
4. **Document functions**: Use docstrings to explain function purpose and parameters
5. **Follow naming conventions**: Use clear, descriptive names
6. **Keep imports organized**: Group imports by standard library, third-party, and local

