"""
NMMC compliance checking functions.
"""
import pandas as pd
from datetime import datetime
from config import CURRENT_YEAR


def check_nmmc_compliance(building: pd.Series, rules: dict, financial_details: dict) -> tuple:
    """
    Checks NMMC compliance rules from the JSON file.
    
    Args:
        building: Series containing building data
        rules: Dictionary containing compliance rules
        financial_details: Dictionary containing financial health details
        
    Returns:
        Tuple of (compliance_score, results_list)
    """
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
                last_inspection_str = building.get('last_fire_safety', '')
                if pd.isna(last_inspection_str) or last_inspection_str == '':
                    condition_met = False
                    details = "No fire safety inspection date found."
                else:
                    last_inspection = pd.to_datetime(last_inspection_str, errors='coerce')
                    if pd.isna(last_inspection):
                        condition_met = False
                        details = f"Invalid date format: {last_inspection_str}"
                    else:
                        days_diff = (today - last_inspection).days
                        condition_met = days_diff <= 365 and days_diff >= 0
                        details = f"Last inspection: {last_inspection.date()} ({days_diff} days ago)"
            
            elif rule_id == "STRUCT_AUDIT":
                last_inspection_str = building.get('last_annual_inspection', '')
                if pd.isna(last_inspection_str) or last_inspection_str == '':
                    condition_met = False
                    details = "No structural audit date found."
                else:
                    last_inspection = pd.to_datetime(last_inspection_str, errors='coerce')
                    if pd.isna(last_inspection):
                        condition_met = False
                        details = f"Invalid date format: {last_inspection_str}"
                    else:
                        # Rule: Older buildings need more frequent checks
                        year_built = building.get('year_built', CURRENT_YEAR)
                        if pd.isna(year_built):
                            year_built = CURRENT_YEAR
                        age = CURRENT_YEAR - year_built
                        required_days = 365 if age > 15 else (365 * 3)
                        days_since = (today - last_inspection).days
                        condition_met = days_since <= required_days and days_since >= 0
                        details = f"Last audit: {last_inspection.date()} ({days_since} days ago). Required every {required_days} days."

            elif rule_id == "RESERVE_FUND":
                reserve_ratio = financial_details.get("Reserve Ratio", 0)
                target = rule['parameters']['min_ratio']
                condition_met = reserve_ratio >= target
                details = f"Current Ratio: {reserve_ratio:.2f}, Target: {target}"
            
            elif rule_id == "WASTE_SEGREGATION":
                # Check boolean column - handle both string and boolean types
                waste_seg = building.get('waste_segregation_implemented', False)
                if isinstance(waste_seg, str):
                    condition_met = waste_seg.lower() in ['true', '1', 'yes']
                else:
                    condition_met = bool(waste_seg)
                details = "Based on society records."
            
            elif rule_id == "SEWAGE_SYSTEM":
                # Check boolean column - handle both string and boolean types
                sewage = building.get('sewage_system_approved', False)
                if isinstance(sewage, str):
                    condition_met = sewage.lower() in ['true', '1', 'yes']
                else:
                    condition_met = bool(sewage)
                details = "Based on NMMC approval records."

            if condition_met:
                pass_count += 1
                results.append({"Rule": description, "Status": "✅ Pass", "Details": details})
            else:
                results.append({"Rule": description, "Status": "❌ Fail", "Details": details})

        except Exception as e:
            results.append({"Rule": description, "Status": "⚠️ Error", "Details": f"Could not check rule: {e}"})

    compliance_score = (pass_count / len(rules['rules'])) * 100 if rules['rules'] else 0
    return compliance_score, results

