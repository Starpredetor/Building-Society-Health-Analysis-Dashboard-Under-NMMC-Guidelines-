"""
Data loading functions with error handling and caching.
"""
import pandas as pd
import json
import streamlit as st


@st.cache_data
def load_csv(file_path: str) -> pd.DataFrame:
    """
    Loads CSV data with error handling and automatic boolean conversion.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        DataFrame with loaded data, or empty DataFrame on error
    """
    try:
        df = pd.read_csv(file_path)
        # Convert boolean columns from string to boolean
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check if column contains boolean strings
                unique_vals = df[col].dropna().unique()
                if set(unique_vals).issubset({'true', 'false', 'True', 'False', True, False}):
                    df[col] = df[col].astype(str).str.lower().map({'true': True, 'false': False})
        return df
    except FileNotFoundError:
        st.error(f"Error: {file_path} not found. Please make sure all data files are in the same directory.")
        return pd.DataFrame()
    except pd.errors.EmptyDataError:
        st.error(f"Error: {file_path} is empty.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading {file_path}: {str(e)}")
        return pd.DataFrame()


@st.cache_data
def load_json(file_path: str) -> dict:
    """
    Loads JSON data with error handling.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary with loaded data, or None on error
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Error: {file_path} not found. Please make sure all data files are in the same directory.")
        return None
    except json.JSONDecodeError as e:
        st.error(f"Error: Could not decode {file_path}. Please check the JSON format. {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error loading {file_path}: {str(e)}")
        return None

