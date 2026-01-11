"""Data processing and merging utilities."""

import pandas as pd
import numpy as np
from typing import Optional

from src.utils.country_codes import get_iso_alpha3, standardize_country_name
from src.data.loaders import (
    load_joshua_project_data,
    load_open_doors_data,
    load_wef_ttdi_data,
    load_action_sports_data,
)


def process_joshua_project_data(df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """Process Joshua Project data, adding ISO codes and cleaning.

    Args:
        df: Optional pre-loaded DataFrame, loads if None

    Returns:
        Processed DataFrame with ISO codes
    """
    if df is None:
        df = load_joshua_project_data()

    if df.empty:
        return df

    # Add ISO codes
    df['iso_alpha_3'] = df['Country'].apply(get_iso_alpha3)

    # Standardize country names
    df['country_name'] = df['Country'].apply(standardize_country_name)

    # Handle missing evangelical percentages (marked as 0.0 but unknown)
    # Keep as is - they are already numeric

    # Rename columns for consistency
    df = df.rename(columns={
        'Population': 'population',
        'Percent Evangelical': 'pct_evangelical',
        'Percent Christian Adherent': 'pct_christian',
        'Percent Unreached': 'pct_unreached',
        'Primary Religion': 'primary_religion',
        'Unreached People Groups': 'unreached_groups',
        'Continent': 'continent',
    })

    return df


def process_open_doors_data(df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """Process Open Doors persecution data.

    Args:
        df: Optional pre-loaded DataFrame, loads if None

    Returns:
        Processed DataFrame with ISO codes
    """
    if df is None:
        df = load_open_doors_data()

    if df.empty:
        return df

    # Add ISO codes
    df['iso_alpha_3'] = df['country'].apply(get_iso_alpha3)

    # Standardize country names
    df['country_name'] = df['country'].apply(standardize_country_name)

    # Rename columns for consistency
    df = df.rename(columns={
        'persecution_score': 'persecution_score',
        'rank': 'persecution_rank',
    })

    return df


def process_wef_ttdi_data(df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """Process WEF TTDI tourism data.

    Args:
        df: Optional pre-loaded DataFrame, loads if None

    Returns:
        Processed DataFrame with standardized columns
    """
    if df is None:
        df = load_wef_ttdi_data()

    if df.empty:
        return df

    # Add ISO codes if not present
    if 'iso_alpha_3' not in df.columns:
        df['iso_alpha_3'] = df['Country'].apply(get_iso_alpha3)

    # Standardize country names
    df['country_name'] = df['Country'].apply(standardize_country_name)

    # Rename columns for consistency
    df = df.rename(columns={
        'Overall_TTDI_Score': 'ttdi_score',
        'Rank': 'ttdi_rank',
        'ISO_Code': 'iso_code_original',
    })

    return df


def merge_all_data() -> pd.DataFrame:
    """Merge all data sources into a single DataFrame.

    Returns:
        Merged DataFrame with all country data
    """
    # Load and process each data source
    joshua_df = process_joshua_project_data()
    open_doors_df = process_open_doors_data()
    wef_df = process_wef_ttdi_data()

    # Start with Joshua Project as base (most complete country list)
    merged = joshua_df.copy()

    # Merge Open Doors data
    if not open_doors_df.empty:
        open_doors_cols = ['iso_alpha_3', 'persecution_score', 'persecution_rank']
        open_doors_subset = open_doors_df[open_doors_cols].copy()
        merged = merged.merge(
            open_doors_subset,
            on='iso_alpha_3',
            how='left'
        )

    # Merge WEF TTDI data
    if not wef_df.empty:
        wef_cols = ['iso_alpha_3', 'ttdi_score', 'ttdi_rank']
        wef_subset = wef_df[wef_cols].copy()
        merged = merged.merge(
            wef_subset,
            on='iso_alpha_3',
            how='left'
        )

    # Fill missing persecution scores with 0 (no persecution data = low persecution)
    # This is a reasonable default for countries not in the WWL top 50
    merged['persecution_score'] = merged['persecution_score'].fillna(0)

    # Calculate legal openness as inverse of persecution
    # Higher openness score = lower persecution
    merged['legal_openness'] = 100 - merged['persecution_score']

    # Fill missing TTDI scores with median
    if 'ttdi_score' in merged.columns:
        median_ttdi = merged['ttdi_score'].median()
        merged['ttdi_score'] = merged['ttdi_score'].fillna(median_ttdi)

    # Merge action sports data
    merged = merge_action_sports(merged)

    return merged


def merge_action_sports(df: pd.DataFrame) -> pd.DataFrame:
    """Merge action sports availability data with main country data.

    Args:
        df: Main country DataFrame with iso_alpha_3 column

    Returns:
        DataFrame with action sports boolean columns added
    """
    action_sports_df = load_action_sports_data()

    if action_sports_df.empty:
        return df

    # Get all action sport columns (excluding country_name and iso_alpha_3)
    sport_columns = [col for col in action_sports_df.columns
                     if col not in ['country_name', 'iso_alpha_3']]

    # Select only necessary columns for merge
    action_sports_subset = action_sports_df[['iso_alpha_3'] + sport_columns].copy()

    # Merge on ISO code
    merged = df.merge(
        action_sports_subset,
        on='iso_alpha_3',
        how='left'
    )

    # Fill any missing sport values with False
    for col in sport_columns:
        if col in merged.columns:
            merged[col] = merged[col].fillna(False).astype(bool)

    return merged


def calculate_religious_need_score(df: pd.DataFrame) -> pd.Series:
    """Calculate religious need score based on Christian demographics.

    Higher score = greater need for outreach (fewer Christians)

    Args:
        df: DataFrame with pct_christian and pct_unreached columns

    Returns:
        Series with religious need scores (0-100)
    """
    # Combine % non-Christian with % unreached
    # More weight on unreached groups as they indicate active need
    pct_non_christian = 100 - df['pct_christian'].fillna(50)
    pct_unreached = df['pct_unreached'].fillna(50)

    # Weighted combination: 60% unreached, 40% non-Christian
    need_score = (0.6 * pct_unreached) + (0.4 * pct_non_christian)

    return need_score.clip(0, 100)


def calculate_missionary_gap_score(df: pd.DataFrame) -> pd.Series:
    """Calculate missionary engagement gap score.

    Higher score = greater gap in missionary engagement

    Args:
        df: DataFrame with unreached_groups and pct_evangelical columns

    Returns:
        Series with missionary gap scores (0-100)
    """
    # Use unreached people groups as primary indicator
    # Normalize by population to get per-capita measure
    unreached = df['unreached_groups'].fillna(0)
    population = df['population'].fillna(1)

    # Unreached groups per million population
    unreached_per_million = (unreached / population) * 1_000_000

    # Also factor in low evangelical presence
    low_evangelical = 100 - (df['pct_evangelical'].fillna(0) * 10)  # Scale 0-10% to 0-100

    # Normalize unreached_per_million to 0-100
    max_upm = unreached_per_million.max()
    if max_upm > 0:
        unreached_normalized = (unreached_per_million / max_upm) * 100
    else:
        unreached_normalized = pd.Series([0] * len(df))

    # Combine: 50% unreached groups, 50% low evangelical
    gap_score = (0.5 * unreached_normalized) + (0.5 * low_evangelical.clip(0, 100))

    return gap_score.clip(0, 100)
