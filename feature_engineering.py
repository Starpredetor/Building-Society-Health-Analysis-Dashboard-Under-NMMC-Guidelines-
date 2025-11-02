"""
Feature engineering for machine learning models.
"""
import pandas as pd
import numpy as np
from config import CURRENT_YEAR, MIN_RESERVE_PER_FLAT_PER_YEAR, AUDIT_RATING_MAP, INCOME_SCORE_MAP


def create_ml_features(buildings_df: pd.DataFrame, residents_df: pd.DataFrame, 
                       transactions_df: pd.DataFrame, repairs_df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates machine learning features from raw data.
    
    Args:
        buildings_df: DataFrame with building data
        residents_df: DataFrame with resident data
        transactions_df: DataFrame with transaction data
        repairs_df: DataFrame with repair data
        
    Returns:
        DataFrame with engineered features for ML
    """
    features_list = []
    
    for _, building in buildings_df.iterrows():
        building_id = building.get('building_id', '')
        if pd.isna(building_id) or building_id == '':
            continue
        
        # Basic building features
        year_built = building.get('year_built', CURRENT_YEAR)
        age = CURRENT_YEAR - year_built if not pd.isna(year_built) else 0
        
        # Financial features
        total_flats = building.get('total_flats', 0)
        total_flats = 0 if pd.isna(total_flats) else total_flats
        
        current_fund = building.get('current_fund', 0)
        current_fund = 0 if pd.isna(current_fund) else current_fund
        
        reserve_fund = building.get('reserve_fund', 0)
        reserve_fund = 0 if pd.isna(reserve_fund) else reserve_fund
        
        monthly_collected = building.get('monthly_maintenance_collected', 0)
        monthly_collected = 0 if pd.isna(monthly_collected) else monthly_collected
        
        monthly_expected = building.get('monthly_maintenance_expected', 0)
        monthly_expected = 0 if pd.isna(monthly_expected) else monthly_expected
        
        # Calculated financial features
        collection_rate = (monthly_collected / monthly_expected * 100) if monthly_expected > 0 else 0
        total_funds = current_fund + reserve_fund
        required_reserve = total_flats * MIN_RESERVE_PER_FLAT_PER_YEAR * max(1, age) if total_flats > 0 else 1
        reserve_ratio = total_funds / required_reserve if required_reserve > 0 else 0
        
        # Structural features
        audit_rating = building.get('structural_audit_rating', '')
        audit_rating_score = AUDIT_RATING_MAP.get(str(audit_rating).upper(), 0) if not pd.isna(audit_rating) else 0
        
        # Repair features
        building_repairs = repairs_df[repairs_df['building_id'] == building_id]
        num_repairs = len(building_repairs)
        num_open_issues = len(building_repairs[building_repairs['status'] == 'Open'])
        num_high_severity = len(building_repairs[
            (building_repairs['status'] == 'Open') & 
            (building_repairs['severity'] == 'High')
        ])
        total_repair_cost = building_repairs['estimated_cost'].sum() if 'estimated_cost' in building_repairs.columns else 0
        
        # Resident features
        building_residents = residents_df[residents_df['building_id'] == building_id]
        num_residents = len(building_residents)
        
        if not building_residents.empty:
            # Payment punctuality
            flats_with_no_dues = len(building_residents[building_residents['maintenance_due_amount'] == 0])
            payment_punctuality = (flats_with_no_dues / total_flats * 100) if total_flats > 0 else 0
            
            # Ownership ratio
            num_owners = len(building_residents[building_residents['owner_or_tenant'] == 'Owner'])
            owner_ratio = (num_owners / total_flats * 100) if total_flats > 0 else 0
            
            # Average dues
            avg_dues = building_residents['maintenance_due_amount'].mean() if 'maintenance_due_amount' in building_residents.columns else 0
            total_dues = building_residents['maintenance_due_amount'].sum() if 'maintenance_due_amount' in building_residents.columns else 0
            
            # Socio-economic features
            income_scores = building_residents['avg_monthly_income'].map(INCOME_SCORE_MAP).fillna(0)
            avg_income_score = income_scores.mean()
            
            # Education mapping
            edu_map = {'High School': 50, 'Graduate': 80, 'Post-Graduate': 100}
            edu_scores = building_residents['education_level'].map(edu_map).fillna(0)
            avg_edu_score = edu_scores.mean()
        else:
            payment_punctuality = 0
            owner_ratio = 0
            avg_dues = 0
            total_dues = 0
            avg_income_score = 0
            avg_edu_score = 0
        
        # Transaction features
        building_transactions = transactions_df[transactions_df['building_id'] == building_id]
        total_expenses = building_transactions[building_transactions['transaction_type'] == 'Expense']['amount'].sum() if not building_transactions.empty else 0
        total_income = building_transactions[building_transactions['transaction_type'] == 'Income']['amount'].sum() if not building_transactions.empty else 0
        expense_categories = building_transactions[building_transactions['transaction_type'] == 'Expense'].groupby('category')['amount'].sum()
        
        # Boolean features
        waste_segregation = 1 if building.get('waste_segregation_implemented', False) else 0
        sewage_approved = 1 if building.get('sewage_system_approved', False) else 0
        
        # Create feature dictionary
        features = {
            'building_id': building_id,
            'age': age,
            'total_flats': total_flats,
            'total_residents': num_residents if not building_residents.empty else 0,
            'current_fund': current_fund,
            'reserve_fund': reserve_fund,
            'total_funds': total_funds,
            'monthly_collected': monthly_collected,
            'monthly_expected': monthly_expected,
            'collection_rate': collection_rate,
            'reserve_ratio': reserve_ratio,
            'audit_rating_score': audit_rating_score,
            'num_repairs': num_repairs,
            'num_open_issues': num_open_issues,
            'num_high_severity': num_high_severity,
            'total_repair_cost': total_repair_cost,
            'payment_punctuality': payment_punctuality,
            'owner_ratio': owner_ratio,
            'avg_dues': avg_dues,
            'total_dues': total_dues,
            'avg_income_score': avg_income_score,
            'avg_edu_score': avg_edu_score,
            'total_expenses': total_expenses,
            'total_income': total_income,
            'waste_segregation': waste_segregation,
            'sewage_approved': sewage_approved,
        }
        
        # Add expense category features
        if not expense_categories.empty:
            for category in ['Security Salaries', 'Utilities', 'Repairs', 'Amenities']:
                features[f'expense_{category.replace(" ", "_").lower()}'] = expense_categories.get(category, 0)
        else:
            for category in ['Security Salaries', 'Utilities', 'Repairs', 'Amenities']:
                features[f'expense_{category.replace(" ", "_").lower()}'] = 0
        
        features_list.append(features)
    
    return pd.DataFrame(features_list)

