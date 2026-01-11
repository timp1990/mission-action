"""Chart components for country detail visualizations."""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List, Optional


def create_score_breakdown_chart(
    country_details: Dict,
    chart_type: str = 'bar'
) -> go.Figure:
    """Create a chart showing score breakdown for a country.

    Args:
        country_details: Dict from get_country_details()
        chart_type: 'bar' or 'radar'

    Returns:
        Plotly Figure object
    """
    scores = country_details.get('scores', {})

    categories = ['Action Sports', 'Outreach', 'Combined']
    values = [
        scores.get('action_sports', 0),
        scores.get('outreach', 0),
        scores.get('combined', 0),
    ]

    if chart_type == 'radar':
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],  # Close the polygon
            theta=categories + [categories[0]],
            fill='toself',
            name=country_details.get('name', 'Country'),
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=False,
        )
    else:  # bar
        fig = px.bar(
            x=categories,
            y=values,
            color=categories,
            color_discrete_map={
                'Action Sports': '#1f77b4',
                'Outreach': '#ff7f0e',
                'Combined': '#2ca02c',
            },
        )
        fig.update_layout(
            yaxis_range=[0, 100],
            showlegend=False,
            xaxis_title='',
            yaxis_title='Score',
        )

    fig.update_layout(
        title=f"Scores for {country_details.get('name', 'Selected Country')}",
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
    )

    return fig


def create_component_breakdown_chart(
    country_details: Dict,
    score_type: str = 'outreach'
) -> go.Figure:
    """Create a chart showing component breakdown for a score.

    Args:
        country_details: Dict from get_country_details()
        score_type: 'action_sports' or 'outreach'

    Returns:
        Plotly Figure object
    """
    components = country_details.get('components', {})

    if score_type == 'outreach':
        # Outreach components
        categories = [
            'Religious Need',
            'Missionary Gap',
            'Legal Openness',
        ]
        # Calculate approximate component values
        pct_christian = components.get('pct_christian', 50)
        pct_unreached = components.get('pct_unreached', 50)
        legal_openness = components.get('legal_openness', 100)

        # Religious need: inverse of Christian percentage
        religious_need = (0.6 * pct_unreached) + (0.4 * (100 - pct_christian))

        # Missionary gap: based on unreached groups and low evangelical
        unreached = components.get('unreached_groups', 0)
        pct_evangelical = components.get('pct_evangelical', 0)
        missionary_gap = 100 - (pct_evangelical * 10)  # Simplified

        values = [
            min(100, max(0, religious_need)),
            min(100, max(0, missionary_gap)),
            min(100, max(0, legal_openness)),
        ]
    else:
        # Action sports - just TTDI for now
        ttdi = components.get('ttdi_score', 3.5)
        # Normalize 1-6 to 0-100
        normalized = ((ttdi - 1) / 5) * 100

        categories = ['Tourism Development Index']
        values = [min(100, max(0, normalized))]

    fig = px.bar(
        x=categories,
        y=values,
        color_discrete_sequence=['#636efa'],
    )

    fig.update_layout(
        yaxis_range=[0, 100],
        xaxis_title='',
        yaxis_title='Score',
        title=f"{score_type.replace('_', ' ').title()} Components",
        height=250,
        margin=dict(l=20, r=20, t=40, b=20),
    )

    return fig


def create_comparison_chart(
    df: pd.DataFrame,
    countries: List[str],
    score_type: str = 'combined'
) -> go.Figure:
    """Create a chart comparing multiple countries.

    Args:
        df: DataFrame with rankings data
        countries: List of country names to compare
        score_type: Type of score to compare

    Returns:
        Plotly Figure object
    """
    # Filter to selected countries
    name_col = 'country_name' if 'country_name' in df.columns else 'Country'
    compare_df = df[df[name_col].isin(countries)].copy()

    if compare_df.empty:
        return go.Figure()

    score_col = f'{score_type}_score'

    fig = px.bar(
        compare_df,
        x=name_col,
        y=score_col,
        color=name_col,
        title=f'{score_type.replace("_", " ").title()} Comparison',
    )

    fig.update_layout(
        yaxis_range=[0, 100],
        xaxis_title='',
        yaxis_title='Score',
        showlegend=False,
        height=300,
    )

    return fig


def create_scatter_plot(
    df: pd.DataFrame,
    x_score: str = 'action_sports_score',
    y_score: str = 'outreach_score',
    size_col: str = None,
    color_col: str = None,
) -> go.Figure:
    """Create a scatter plot of two scores.

    Args:
        df: DataFrame with rankings data
        x_score: Column for x-axis
        y_score: Column for y-axis
        size_col: Column for bubble size (optional)
        color_col: Column for color (optional)

    Returns:
        Plotly Figure object
    """
    name_col = 'country_name' if 'country_name' in df.columns else 'Country'

    # Build arguments
    scatter_args = {
        'x': x_score,
        'y': y_score,
        'hover_name': name_col,
        'title': 'Action Sports vs Outreach Opportunity',
    }

    if size_col and size_col in df.columns:
        scatter_args['size'] = size_col
        scatter_args['size_max'] = 40

    if color_col and color_col in df.columns:
        scatter_args['color'] = color_col

    fig = px.scatter(df, **scatter_args)

    fig.update_layout(
        xaxis_title='Action Sports Score',
        yaxis_title='Outreach Score',
        xaxis_range=[0, 105],
        yaxis_range=[0, 105],
        height=500,
    )

    # Add quadrant lines
    fig.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=50, line_dash="dash", line_color="gray", opacity=0.5)

    return fig


def create_ranking_distribution(
    df: pd.DataFrame,
    score_type: str = 'combined'
) -> go.Figure:
    """Create a histogram of score distribution.

    Args:
        df: DataFrame with rankings data
        score_type: Type of score

    Returns:
        Plotly Figure object
    """
    score_col = f'{score_type}_score'

    fig = px.histogram(
        df,
        x=score_col,
        nbins=20,
        title=f'{score_type.replace("_", " ").title()} Score Distribution',
    )

    fig.update_layout(
        xaxis_title='Score',
        yaxis_title='Number of Countries',
        xaxis_range=[0, 100],
        height=300,
    )

    return fig
