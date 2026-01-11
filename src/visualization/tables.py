"""Rankings table visualization components."""

import streamlit as st
import pandas as pd
from typing import List, Optional


def create_rankings_table(
    df: pd.DataFrame,
    score_type: str = 'combined',
    columns: List[str] = None,
    height: int = 400,
    search_term: str = None,
) -> pd.DataFrame:
    """Create a formatted rankings table for display.

    Args:
        df: DataFrame with rankings data
        score_type: Which ranking to sort by
        columns: Columns to display (uses defaults if None)
        height: Height of the table in pixels
        search_term: Optional search term to filter countries

    Returns:
        Filtered and formatted DataFrame
    """
    if columns is None:
        columns = [
            'country_name',
            f'{score_type}_rank',
            f'{score_type}_score',
            'action_sports_score',
            'outreach_score',
            'combined_score',
        ]

    # Filter to existing columns
    available_cols = [c for c in columns if c in df.columns]

    if not available_cols:
        # Fallback to basic columns
        available_cols = ['Country', 'combined_score', 'combined_rank']
        available_cols = [c for c in available_cols if c in df.columns]

    display_df = df[available_cols].copy()

    # Apply search filter
    if search_term:
        name_col = 'country_name' if 'country_name' in display_df.columns else 'Country'
        if name_col in display_df.columns:
            display_df = display_df[
                display_df[name_col].str.lower().str.contains(
                    search_term.lower(), na=False
                )
            ]

    # Sort by rank
    rank_col = f'{score_type}_rank'
    if rank_col in display_df.columns:
        display_df = display_df.sort_values(rank_col)

    return display_df


def format_rankings_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Format a rankings DataFrame for better display.

    Args:
        df: Raw rankings DataFrame

    Returns:
        Formatted DataFrame
    """
    formatted = df.copy()

    # Rename columns for display
    column_renames = {
        'country_name': 'Country',
        'combined_rank': 'Rank',
        'combined_score': 'Combined',
        'action_sports_rank': 'AS Rank',
        'action_sports_score': 'Action Sports',
        'outreach_rank': 'Outreach Rank',
        'outreach_score': 'Outreach',
        'iso_alpha_3': 'ISO',
        'continent': 'Continent',
        'population': 'Population',
        'primary_religion': 'Religion',
    }

    formatted = formatted.rename(columns=column_renames)

    # Format population with commas
    if 'Population' in formatted.columns:
        formatted['Population'] = formatted['Population'].apply(
            lambda x: f"{int(x):,}" if pd.notna(x) else ""
        )

    return formatted


def display_rankings_table(
    df: pd.DataFrame,
    score_type: str = 'combined',
    search_enabled: bool = True,
    page_size: int = 20,
) -> Optional[str]:
    """Display an interactive rankings table in Streamlit.

    Args:
        df: DataFrame with rankings data
        score_type: Which ranking to display/sort by
        search_enabled: Whether to show search box
        page_size: Number of rows per page

    Returns:
        Selected country name if a row is clicked, None otherwise
    """
    search_term = None

    if search_enabled:
        search_term = st.text_input(
            "Search countries",
            placeholder="Type to search...",
            key=f"search_{score_type}"
        )

    # Get filtered table
    table_df = create_rankings_table(
        df,
        score_type=score_type,
        search_term=search_term
    )

    # Format for display
    display_df = format_rankings_dataframe(table_df)

    # Display with Streamlit
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400,
        hide_index=True,
    )

    return None


def get_column_config(score_type: str = 'combined') -> dict:
    """Get Streamlit column configuration for rankings table.

    Args:
        score_type: Type of score being displayed

    Returns:
        Dict of column configurations
    """
    return {
        'Country': st.column_config.TextColumn(
            'Country',
            width='medium',
        ),
        'Rank': st.column_config.NumberColumn(
            'Rank',
            format='%d',
            width='small',
        ),
        'Combined': st.column_config.ProgressColumn(
            'Combined',
            min_value=0,
            max_value=100,
            format='%.1f',
        ),
        'Action Sports': st.column_config.ProgressColumn(
            'Action Sports',
            min_value=0,
            max_value=100,
            format='%.1f',
        ),
        'Outreach': st.column_config.ProgressColumn(
            'Outreach',
            min_value=0,
            max_value=100,
            format='%.1f',
        ),
        'Population': st.column_config.TextColumn(
            'Population',
            width='small',
        ),
    }
