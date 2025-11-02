"""
Views module for UI components.
"""
from .overview import render_overview_tab
from .building_detail import render_building_detail_tab
from .compliance import render_compliance_tab
from .map_view import render_map_tab
from .ml_insights import render_ml_insights_tab
from .add_building import render_add_building_tab, render_add_resident_tab, render_add_transaction_tab

__all__ = [
    'render_overview_tab',
    'render_building_detail_tab',
    'render_compliance_tab',
    'render_map_tab',
    'render_ml_insights_tab',
    'render_add_building_tab',
    'render_add_resident_tab',
    'render_add_transaction_tab'
]

