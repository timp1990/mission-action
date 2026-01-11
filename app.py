"""
Mission-Action: Strategic Outreach Opportunities Platform

A data visualization platform combining extreme sports tourism potential
with Christian outreach opportunities by country.
"""

import streamlit as st
import pandas as pd
from pathlib import Path

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent))

from src.data.loaders import load_processed_data, save_processed_data
from src.data.processors import merge_all_data
from src.scoring.combined import generate_rankings, get_country_details, get_top_countries
from src.visualization.maps import create_choropleth
from src.visualization.tables import display_rankings_table, format_rankings_dataframe
from src.visualization.charts import (
    create_score_breakdown_chart,
    create_component_breakdown_chart,
    create_scatter_plot,
)


# Page configuration
st.set_page_config(
    page_title="Mission-Action: Strategic Outreach Opportunities",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_data(ttl=3600)
def load_data():
    """Load or compute rankings data."""
    # Try to load pre-computed data
    df = load_processed_data()

    if df is None:
        # Compute rankings from raw data
        with st.spinner("Computing rankings from raw data..."):
            merged = merge_all_data()
            if merged.empty:
                st.error("No data available. Please check data files in data/raw/")
                return pd.DataFrame()
            df = generate_rankings(merged)
            save_processed_data(df)

    return df


def render_header():
    """Render the page header."""
    st.title("Mission-Action")
    st.markdown("""
    **Combining Extreme Sports Potential and Christian Outreach Opportunities by Country**

    This platform identifies countries where adventure tourism and outreach potential align,
    helping you find strategic locations for mission work through adventure sports.
    """)

    # Data info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Countries Analyzed", "230+")
    with col2:
        st.metric("Data Sources", "4")
    with col3:
        st.metric("Last Updated", "January 2025")


def render_map_section(df: pd.DataFrame, score_type: str):
    """Render the choropleth map section."""
    st.subheader("World Map")

    try:
        fig = create_choropleth(df, score_type=score_type, height=500)
        st.plotly_chart(fig, use_container_width=True, key=f"map_{score_type}")
    except Exception as e:
        st.error(f"Error rendering map: {e}")


def render_rankings_section(df: pd.DataFrame, score_type: str):
    """Render the rankings table section."""
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Country Rankings")

        # Search box with unique key per tab
        search = st.text_input(
            "Search countries",
            placeholder="Type to search...",
            key=f"search_{score_type}"
        )

        # Filter data
        filtered_df = df.copy()
        if search:
            name_col = 'country_name' if 'country_name' in df.columns else 'Country'
            filtered_df = df[
                df[name_col].str.lower().str.contains(search.lower(), na=False)
            ]

        # Display table - use unique columns to avoid duplicates
        display_cols = ['country_name', f'{score_type}_rank', f'{score_type}_score']
        # Add other scores only if they're different from the current score_type
        if score_type != 'action_sports':
            display_cols.append('action_sports_score')
        if score_type != 'outreach':
            display_cols.append('outreach_score')
        if score_type != 'combined':
            display_cols.append('combined_score')
        display_cols.append('continent')

        available_cols = [c for c in display_cols if c in filtered_df.columns]

        formatted = format_rankings_dataframe(filtered_df[available_cols])
        st.dataframe(
            formatted,
            use_container_width=True,
            height=400,
            hide_index=True,
            key=f"rankings_table_{score_type}"
        )

    with col2:
        st.subheader("Top 10 Countries")

        top_10 = get_top_countries(df, score_type=score_type, top_n=10)
        name_col = 'country_name' if 'country_name' in top_10.columns else 'Country'

        for i, (_, row) in enumerate(top_10.iterrows(), 1):
            score = row.get(f'{score_type}_score', 0)
            st.markdown(f"**{i}. {row[name_col]}** — {score:.1f}")


def render_country_detail(df: pd.DataFrame, country_name: str):
    """Render detailed information for a selected country."""
    st.subheader(f"Country Details: {country_name}")

    details = get_country_details(df, country_name)

    if details is None:
        st.warning(f"No data found for {country_name}")
        return

    # Basic info
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### Scores")
        scores = details.get('scores', {})
        st.metric("Combined", f"{scores.get('combined', 0):.1f}")
        st.metric("Action Sports", f"{scores.get('action_sports', 0):.1f}")
        st.metric("Outreach", f"{scores.get('outreach', 0):.1f}")

    with col2:
        st.markdown("### Rankings")
        ranks = details.get('ranks', {})
        st.metric("Combined Rank", f"#{ranks.get('combined', '-')}")
        st.metric("Action Sports Rank", f"#{ranks.get('action_sports', '-')}")
        st.metric("Outreach Rank", f"#{ranks.get('outreach', '-')}")

    with col3:
        st.markdown("### Demographics")
        comps = details.get('components', {})
        st.write(f"**Population:** {details.get('population', 0):,}")
        st.write(f"**Primary Religion:** {details.get('primary_religion', 'N/A')}")
        st.write(f"**% Christian:** {comps.get('pct_christian', 0):.1f}%")
        st.write(f"**% Unreached:** {comps.get('pct_unreached', 0):.1f}%")

    # Score breakdown chart
    st.markdown("### Score Breakdown")
    fig = create_score_breakdown_chart(details, chart_type='bar')
    st.plotly_chart(fig, use_container_width=True)


def render_methodology():
    """Render the methodology section."""
    st.markdown("## Methodology")

    with st.expander("Scoring Methodology", expanded=False):
        st.markdown("""
        ### Action Sports Score (0-100)

        Based on the WEF Travel & Tourism Development Index, incorporating:
        - **Natural Resources** (30%) - Mountains, coastlines, terrain diversity
        - **Safety & Accessibility** (25%) - Political stability, infrastructure
        - **Tourism Infrastructure** (25%) - Hotels, transport, services
        - **Sustainability & Reputation** (20%) - Adventure brand, sustainability

        ### Christian Outreach Score (0-100)

        Combines three key dimensions:
        - **Religious Demographics** (40%) - % non-Christian, unreached populations
        - **Missionary Gap** (25%) - Current engagement vs. need
        - **Legal Openness** (35%) - Religious freedom, inverse of persecution

        ### Combined Score

        The combined score is calculated by multiplying Action Sports and Outreach
        scores, then normalizing to 0-100:

        ```
        Combined = (Action Sports × Outreach) / 100
        ```

        This ensures countries must score well in BOTH dimensions to rank highly.
        """)

    with st.expander("Data Sources", expanded=False):
        st.markdown("""
        - **Joshua Project** - Religious demographics, unreached population data
        - **Open Doors World Watch List 2025** - Christian persecution scores
        - **WEF Travel & Tourism Development Index 2024** - Tourism infrastructure
        - **Pew Research Center** - Religious composition data

        Data is refreshed annually.
        """)

    with st.expander("Limitations", expanded=False):
        st.markdown("""
        - Religious demographics are estimates with varying accuracy
        - Persecution scores only cover top 50 most affected countries
        - Tourism data may not capture emerging adventure destinations
        - Combined score may underweight countries strong in one dimension
        """)


def render_scatter_analysis(df: pd.DataFrame):
    """Render scatter plot analysis."""
    st.subheader("Score Distribution Analysis")

    fig = create_scatter_plot(
        df,
        x_score='action_sports_score',
        y_score='outreach_score',
        color_col='continent',
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    *Countries in the upper-right quadrant have both high action sports
    potential AND high outreach opportunity — these are prime targets for
    mission work through adventure sports.*
    """)


def main():
    """Main application entry point."""
    # Load data
    df = load_data()

    if df.empty:
        st.error("Unable to load data. Please ensure data files exist in data/raw/")
        return

    # Header
    render_header()

    st.divider()

    # Tab navigation
    tab_combined, tab_action, tab_outreach, tab_analysis, tab_methodology = st.tabs([
        "Combined Rankings",
        "Action Sports",
        "Outreach Opportunity",
        "Analysis",
        "Methodology"
    ])

    with tab_combined:
        render_map_section(df, 'combined')
        render_rankings_section(df, 'combined')

        # Country selector for details
        st.divider()
        name_col = 'country_name' if 'country_name' in df.columns else 'Country'
        countries = sorted(df[name_col].dropna().unique())
        selected = st.selectbox("Select a country for details:", [""] + list(countries))
        if selected:
            render_country_detail(df, selected)

    with tab_action:
        render_map_section(df, 'action_sports')
        render_rankings_section(df, 'action_sports')

    with tab_outreach:
        render_map_section(df, 'outreach')
        render_rankings_section(df, 'outreach')

    with tab_analysis:
        render_scatter_analysis(df)

        st.divider()

        # Continent breakdown
        st.subheader("Scores by Continent")
        if 'continent' in df.columns:
            continent_avg = df.groupby('continent').agg({
                'action_sports_score': 'mean',
                'outreach_score': 'mean',
                'combined_score': 'mean',
            }).round(1)
            st.dataframe(continent_avg, use_container_width=True)

    with tab_methodology:
        render_methodology()

    # Footer
    st.divider()
    st.markdown("""
    ---
    *Data sources: Joshua Project, Open Doors, WEF TTDI 2024, Pew Research*

    **Mission-Action** | Connecting Adventure Sports with Strategic Outreach
    """)


if __name__ == "__main__":
    main()
