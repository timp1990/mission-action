"""Choropleth map visualization components using Plotly."""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Optional


# Color scales for different score types
COLOR_SCALES = {
    'combined': 'Viridis',
    'action_sports': 'Blues',
    'outreach': 'Oranges',
}

# Titles for different score types
SCORE_TITLES = {
    'combined': 'Combined Score (Action Sports × Outreach)',
    'action_sports': 'Action Sports Score',
    'outreach': 'Christian Outreach Opportunity Score',
}


def create_choropleth(
    df: pd.DataFrame,
    score_type: str = 'combined',
    height: int = 500,
    show_colorbar: bool = True,
) -> go.Figure:
    """Create a world choropleth map for the specified score type.

    Args:
        df: DataFrame with country data including iso_alpha_3 and scores
        score_type: Type of score to display ('combined', 'action_sports', 'outreach')
        height: Height of the figure in pixels
        show_colorbar: Whether to show the color bar

    Returns:
        Plotly Figure object
    """
    score_col = f"{score_type}_score"
    rank_col = f"{score_type}_rank"

    if score_col not in df.columns:
        raise ValueError(f"Score column '{score_col}' not found in DataFrame")

    # Prepare data for display
    plot_df = df.copy()

    # Get country names for display
    if 'country_name' in plot_df.columns:
        name_col = 'country_name'
    elif 'Country' in plot_df.columns:
        name_col = 'Country'
    else:
        name_col = 'iso_alpha_3'

    # Build hover template
    hover_data = {
        'iso_alpha_3': False,
        score_col: ':.1f',
    }

    if rank_col in plot_df.columns:
        hover_data[rank_col] = True

    # Create choropleth
    fig = px.choropleth(
        plot_df,
        locations='iso_alpha_3',
        color=score_col,
        hover_name=name_col,
        hover_data=hover_data,
        color_continuous_scale=COLOR_SCALES.get(score_type, 'Viridis'),
        title=SCORE_TITLES.get(score_type, f'{score_type.title()} Score'),
        labels={score_col: 'Score', rank_col: 'Rank'},
    )

    # Update layout
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor='lightgray',
            showland=True,
            landcolor='white',
            showocean=True,
            oceancolor='lightblue',
            projection_type='natural earth',
            bgcolor='rgba(0,0,0,0)',
        ),
        height=height,
        margin=dict(l=0, r=0, t=40, b=0),
        coloraxis_colorbar=dict(
            title='Score',
            tickvals=[0, 25, 50, 75, 100],
            ticktext=['0', '25', '50', '75', '100'],
        ) if show_colorbar else None,
    )

    # Update color axis range
    fig.update_coloraxes(cmin=0, cmax=100)

    return fig


def create_comparison_map(
    df: pd.DataFrame,
    score_types: list = None,
    height: int = 400,
) -> dict:
    """Create multiple choropleth maps for comparison.

    Args:
        df: DataFrame with country data
        score_types: List of score types to create maps for
        height: Height of each figure

    Returns:
        Dict mapping score type to Figure
    """
    if score_types is None:
        score_types = ['combined', 'action_sports', 'outreach']

    maps = {}
    for score_type in score_types:
        try:
            maps[score_type] = create_choropleth(
                df,
                score_type=score_type,
                height=height,
            )
        except ValueError:
            continue

    return maps


def create_region_zoom_map(
    df: pd.DataFrame,
    region: str,
    score_type: str = 'combined',
    height: int = 400,
) -> go.Figure:
    """Create a choropleth map zoomed to a specific region.

    Args:
        df: DataFrame with country data
        region: Region to zoom to ('africa', 'asia', 'europe', 'americas', 'oceania')
        score_type: Type of score to display
        height: Height of the figure

    Returns:
        Plotly Figure object
    """
    # Region scope mappings
    region_scopes = {
        'africa': 'africa',
        'asia': 'asia',
        'europe': 'europe',
        'americas': 'north america',  # Plotly uses 'north america' or 'south america'
        'oceania': 'world',  # No specific Oceania scope, use world
    }

    scope = region_scopes.get(region.lower(), 'world')

    fig = create_choropleth(df, score_type=score_type, height=height)

    fig.update_layout(
        geo=dict(
            scope=scope if scope != 'world' else None,
            projection_type='natural earth' if scope == 'world' else None,
        )
    )

    return fig


def highlight_country(
    fig: go.Figure,
    iso_code: str,
    color: str = 'red',
) -> go.Figure:
    """Add a highlight border around a specific country.

    Args:
        fig: Existing Plotly Figure
        iso_code: ISO alpha-3 code of country to highlight
        color: Border color

    Returns:
        Updated Figure
    """
    # This would require adding a separate trace with the country boundary
    # For simplicity, we'll just note this as a future enhancement
    return fig
