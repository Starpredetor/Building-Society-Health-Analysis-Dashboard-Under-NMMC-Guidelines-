"""
Health calculation functions for buildings.
"""
import pandas as pd
from config import (
    CURRENT_YEAR, MIN_RESERVE_PER_FLAT_PER_YEAR,
    FINANCIAL_WEIGHTS, STRUCTURAL_WEIGHTS, PEOPLE_WEIGHTS,
    INCOME_SCORE_MAP, EDUCATION_SCORE_MAP, AUDIT_RATING_MAP
)


def calculate_financial_health(building: pd.Series, transactions_df: pd.DataFrame, 
                               residents_df: pd.DataFrame) -> tuple:
    """
    Calculates the financial health score for a single building.
    
    Args:
        building: Series containing building data
        transactions_df: DataFrame with transaction data
        residents_df: DataFrame with resident data
        
    Returns:
        Tuple of (financial_score, details_dict)
    """
    if building.empty:
        return 0, {}

    # 1. Collection Rate
    monthly_expected = building.get('monthly_maintenance_expected', 0)
    monthly_collected = building.get('monthly_maintenance_collected', 0)
    
    # Handle NaN values
    if pd.isna(monthly_expected):
        monthly_expected = 0
    if pd.isna(monthly_collected):
        monthly_collected = 0
    
    if monthly_expected == 0:
        collection_rate = 0
    else:
        collection_rate = (monthly_collected / monthly_expected) * 100
    
    # 2. Reserve Ratio
    year_built = building.get('year_built', 0)
    total_flats = building.get('total_flats', 0)
    current_fund = building.get('current_fund', 0)
    reserve_fund = building.get('reserve_fund', 0)
    
    # Handle NaN values
    if pd.isna(current_fund):
        current_fund = 0
    if pd.isna(reserve_fund):
        reserve_fund = 0
    if pd.isna(year_built):
        year_built = CURRENT_YEAR
    if pd.isna(total_flats):
        total_flats = 0
    
    total_funds = current_fund + reserve_fund
    
    if year_built <= 0 or total_flats <= 0:
        required_reserve = 1
        reserve_ratio = 0
    else:
        age = CURRENT_YEAR - year_built
        required_reserve = total_flats * MIN_RESERVE_PER_FLAT_PER_YEAR * max(1, age)
        reserve_ratio = total_funds / required_reserve if required_reserve > 0 else 0.0
    
    reserve_ratio_score = min(100, (reserve_ratio * 100))  # Cap at 100

    # 3. Payment Punctuality
    building_residents = residents_df[residents_df['building_id'] == building['building_id']]
    total_flats_for_calc = building.get('total_flats', 0)
    if pd.isna(total_flats_for_calc):
        total_flats_for_calc = 0
    
    if not building_residents.empty and total_flats_for_calc > 0:
        flats_with_no_dues = building_residents[building_residents['maintenance_due_amount'] == 0].shape[0]
        payment_punctuality = (flats_with_no_dues / total_flats_for_calc) * 100
    else:
        payment_punctuality = 0

    # 4. Expense Distribution (for detailed view)
    building_expenses = transactions_df[
        (transactions_df['building_id'] == building['building_id']) &
        (transactions_df['transaction_type'] == 'Expense')
    ]
    expense_dist = building_expenses.groupby('category')['amount'].sum().reset_index()

    # Final Score (Weighted Average)
    financial_score = (
        collection_rate * FINANCIAL_WEIGHTS['collection_rate'] +
        reserve_ratio_score * FINANCIAL_WEIGHTS['reserve_ratio'] +
        payment_punctuality * FINANCIAL_WEIGHTS['payment_punctuality']
    )
    
    details = {
        "Collection Rate (%)": collection_rate,
        "Total Funds (₹)": total_funds,
        "Required Reserve (₹)": required_reserve,
        "Reserve Ratio": reserve_ratio,
        "Payment Punctuality (%)": payment_punctuality,
        "Expense Distribution": expense_dist
    }
    
    return max(0, min(100, financial_score)), details


def calculate_structural_health(building: pd.Series, repairs_df: pd.DataFrame) -> tuple:
    """
    Calculates the structural health score for a single building.
    
    Args:
        building: Series containing building data
        repairs_df: DataFrame with repair data
        
    Returns:
        Tuple of (structural_score, details_dict)
    """
    if building.empty:
        return 0, {}

    # 1. Age Score
    year_built = building.get('year_built', 0)
    if pd.isna(year_built) or year_built <= 0:
        age_score = 0
        age = 0
    else:
        age = CURRENT_YEAR - year_built
        age_score = max(0, 100 - (age * 1.5))  # Penalize older buildings

    # 2. Structural Audit Rating Score
    audit_rating = building.get('structural_audit_rating', '')
    if pd.isna(audit_rating) or audit_rating == '':
        audit_rating_score = 0
    else:
        audit_rating_score = AUDIT_RATING_MAP.get(str(audit_rating).upper(), 0)

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
    structural_score = (
        age_score * STRUCTURAL_WEIGHTS['age'] +
        audit_rating_score * STRUCTURAL_WEIGHTS['audit_rating'] +
        repair_score * STRUCTURAL_WEIGHTS['repairs']
    )
    
    details = {
        "Building Age (Years)": age,
        "Audit Rating": building.get('structural_audit_rating', 'N/A'),
        "Open Issues": num_open_issues,
        "High Severity Issues": num_high_severity,
        "Repair Log": building_repairs
    }
    
    return max(0, min(100, structural_score)), details


def calculate_people_score(building: pd.Series, residents_df: pd.DataFrame) -> tuple:
    """
    Calculates the 'Decency Index' / People Score.
    
    Args:
        building: Series containing building data
        residents_df: DataFrame with resident data
        
    Returns:
        Tuple of (people_score, details_dict)
    """
    if building.empty:
        return 0, {}
        
    building_residents = residents_df[residents_df['building_id'] == building['building_id']]
    if building_residents.empty:
        return 0, {}

    # 1. Payment Punctuality (re-calculated here for direct use)
    total_flats_for_calc = building.get('total_flats', 0)
    if pd.isna(total_flats_for_calc):
        total_flats_for_calc = 0
    
    flats_with_no_dues = building_residents[building_residents['maintenance_due_amount'] == 0].shape[0]
    if total_flats_for_calc > 0:
        payment_punctuality = (flats_with_no_dues / total_flats_for_calc) * 100
    else:
        payment_punctuality = 0

    # 2. Ownership Ratio
    num_owners = building_residents[building_residents['owner_or_tenant'] == 'Owner'].shape[0]
    if total_flats_for_calc > 0:
        owner_ratio = (num_owners / total_flats_for_calc) * 100
    else:
        owner_ratio = 0

    # 3. Socio-Economic Score
    building_residents_copy = building_residents.copy()
    building_residents_copy['income_score'] = building_residents_copy['avg_monthly_income'].map(
        INCOME_SCORE_MAP
    ).fillna(0)
    building_residents_copy['edu_score'] = building_residents_copy['education_level'].map(
        EDUCATION_SCORE_MAP
    ).fillna(0)
    
    avg_income_score = building_residents_copy['income_score'].mean()
    avg_edu_score = building_residents_copy['edu_score'].mean()
    
    socio_economic_score = (avg_income_score * 0.6) + (avg_edu_score * 0.4)
    
    # Final Score (Weighted Average)
    people_score = (
        payment_punctuality * PEOPLE_WEIGHTS['payment_punctuality'] +
        owner_ratio * PEOPLE_WEIGHTS['owner_ratio'] +
        socio_economic_score * PEOPLE_WEIGHTS['socio_economic']
    )
    
    details = {
        "Payment Punctuality (%)": payment_punctuality,
        "Owner-Tenant Ratio (%)": owner_ratio,
        "Avg. Income Score": avg_income_score,
        "Avg. Education Score": avg_edu_score,
        "Resident Details": building_residents
    }

    return max(0, min(100, people_score)), details

