"""Data loading functions with Streamlit caching."""

import streamlit as st
import pandas as pd
from pathlib import Path
from typing import Optional


# Get the data directory path
DATA_DIR = Path(__file__).parent.parent.parent / "data"


@st.cache_data(ttl=3600)
def load_joshua_project_data() -> pd.DataFrame:
    """Load Joshua Project country-level religious data.

    Returns:
        DataFrame with columns: Country, Continent, Population,
        Percent Evangelical, Percent Christian Adherent, Percent Unreached,
        Primary Religion, Unreached People Groups
    """
    file_path = DATA_DIR / "raw" / "joshua_project_countries.csv"

    if not file_path.exists():
        st.error(f"Joshua Project data not found at {file_path}")
        return pd.DataFrame()

    df = pd.read_csv(file_path)

    # Convert percentage strings to floats
    pct_columns = ['Percent Evangelical', 'Percent Christian Adherent', 'Percent Unreached']
    for col in pct_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df


@st.cache_data(ttl=3600)
def load_open_doors_data() -> pd.DataFrame:
    """Load Open Doors World Watch List persecution data.

    Returns:
        DataFrame with columns: rank, country, persecution_score
    """
    file_path = DATA_DIR / "raw" / "open_doors_wwl_2025.csv"

    if not file_path.exists():
        st.error(f"Open Doors data not found at {file_path}")
        return pd.DataFrame()

    df = pd.read_csv(file_path)
    return df


@st.cache_data(ttl=3600)
def load_wef_ttdi_data() -> pd.DataFrame:
    """Load WEF Travel & Tourism Development Index data.

    Returns:
        DataFrame with columns: Rank, Country, ISO_Code, Overall_TTDI_Score
    """
    file_path = DATA_DIR / "raw" / "wef_ttdi_2024.csv"

    if not file_path.exists():
        st.error(f"WEF TTDI data not found at {file_path}")
        return pd.DataFrame()

    df = pd.read_csv(file_path)
    return df


@st.cache_data(ttl=3600)
def load_processed_data() -> Optional[pd.DataFrame]:
    """Load the processed combined rankings data.

    Returns:
        DataFrame with all scores and rankings, or None if not found
    """
    file_path = DATA_DIR / "processed" / "combined_rankings.parquet"

    if not file_path.exists():
        return None

    return pd.read_parquet(file_path)


@st.cache_data
def load_geojson() -> dict:
    """Load world countries GeoJSON for choropleth maps.

    Returns:
        GeoJSON dictionary
    """
    import json

    file_path = DATA_DIR / "geojson" / "countries.geojson"

    if not file_path.exists():
        # Fall back to natural earth data via URL
        import requests
        url = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Save for future use
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(response.text)

        return response.json()

    with open(file_path, 'r') as f:
        return json.load(f)


def save_processed_data(df: pd.DataFrame, filename: str = "combined_rankings.parquet") -> None:
    """Save processed data to parquet format.

    Args:
        df: DataFrame to save
        filename: Output filename
    """
    output_path = DATA_DIR / "processed" / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
