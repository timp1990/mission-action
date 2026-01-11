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


@st.cache_data(ttl=3600)
def load_action_sports_data() -> pd.DataFrame:
    """Load action sports availability by country.

    Returns:
        DataFrame with columns: country_name, iso_alpha_3, plus 50 boolean sport columns
    """
    file_path = DATA_DIR / "raw" / "action_sports_by_country.csv"

    if not file_path.exists():
        return pd.DataFrame()

    return pd.read_csv(file_path)


# Mapping from display names to column names for action sports
ACTION_SPORTS_MAPPING = {
    'Surfing': 'surfing',
    'Kitesurfing': 'kitesurfing',
    'Windsurfing': 'windsurfing',
    'Scuba Diving': 'scuba_diving',
    'Snorkeling': 'snorkeling',
    'Stand-up Paddleboarding': 'sup',
    'Bodyboarding': 'bodyboarding',
    'Jet Skiing': 'jet_skiing',
    'Wakeboarding': 'wakeboarding',
    'Cliff Diving': 'cliff_diving',
    'Skiing': 'skiing',
    'Snowboarding': 'snowboarding',
    'Freestyle Skiing': 'freestyle_skiing',
    'Backcountry Skiing': 'backcountry_skiing',
    'Ice Climbing': 'ice_climbing',
    'Snowmobiling': 'snowmobiling',
    'Cross-country Skiing': 'xc_skiing',
    'Heli-skiing': 'heli_skiing',
    'Rock Climbing': 'rock_climbing',
    'Mountaineering': 'mountaineering',
    'Paragliding': 'paragliding',
    'Hang Gliding': 'hang_gliding',
    'Bungee Jumping': 'bungee_jumping',
    'Via Ferrata': 'via_ferrata',
    'Canyoning': 'canyoning',
    'Zip-lining': 'ziplining',
    'White Water Rafting': 'white_water_rafting',
    'Kayaking': 'kayaking',
    'Canoeing': 'canoeing',
    'Jet Boating': 'jet_boating',
    'Lake Wakeboarding': 'lake_wakeboarding',
    'Water Skiing': 'water_skiing',
    'Tubing': 'tubing',
    'Flyboarding': 'flyboarding',
    'Skateboarding': 'skateboarding',
    'BMX': 'bmx',
    'Mountain Biking': 'mountain_biking',
    'Motocross': 'motocross',
    'Inline Skating': 'inline_skating',
    'Parkour': 'parkour',
    'Trail Running': 'trail_running',
    'ATV/Quad Biking': 'atv_quad',
    'Go-karting': 'go_karting',
    'Obstacle Course Racing': 'obstacle_racing',
    'Skydiving': 'skydiving',
    'Base Jumping': 'base_jumping',
    'Wingsuit Flying': 'wingsuit',
    'Hot Air Ballooning': 'hot_air_ballooning',
    'Powered Paragliding': 'powered_paragliding',
    'Indoor Skydiving': 'indoor_skydiving',
}


def get_action_sports_list() -> list:
    """Get list of all action sports display names for filter dropdown.

    Returns:
        List of action sport display names in alphabetical order
    """
    return sorted(ACTION_SPORTS_MAPPING.keys())


def sport_display_to_column(display_name: str) -> str:
    """Convert action sport display name to column name.

    Args:
        display_name: Human-readable sport name (e.g., 'Scuba Diving')

    Returns:
        Column name in the data (e.g., 'scuba_diving')
    """
    return ACTION_SPORTS_MAPPING.get(display_name, display_name.lower().replace(' ', '_'))
