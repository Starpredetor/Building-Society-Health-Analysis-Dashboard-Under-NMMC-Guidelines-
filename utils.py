"""
Utility functions for the Building Health Dashboard.
"""
from config import BHI_WEIGHTS, BHI_COLOR_THRESHOLDS


def calculate_bhi(financial_score: float, structural_score: float, people_score: float) -> float:
    """
    Calculates the final Building Health Index (BHI).
    
    Args:
        financial_score: Financial health score (0-100)
        structural_score: Structural health score (0-100)
        people_score: People/Resident score (0-100)
        
    Returns:
        BHI score (0-100)
    """
    bhi = (
        financial_score * BHI_WEIGHTS['financial'] +
        structural_score * BHI_WEIGHTS['structural'] +
        people_score * BHI_WEIGHTS['people']
    )
    return max(0, min(100, bhi))


def get_bhi_color(bhi: float) -> str:
    """
    Returns a color based on the BHI score.
    
    Args:
        bhi: Building Health Index score (0-100)
        
    Returns:
        Color string ('green', 'orange', or 'red')
    """
    if bhi >= BHI_COLOR_THRESHOLDS['green']:
        return 'green'
    elif bhi >= BHI_COLOR_THRESHOLDS['orange']:
        return 'orange'
    else:
        return 'red'

