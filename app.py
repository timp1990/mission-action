"""
Mission-Action: Strategic Outreach Opportunities Platform

A data visualization platform combining extreme sports tourism potential
with Christian outreach opportunities by country.
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent))

from src.data.loaders import load_processed_data, save_processed_data
from src.data.processors import merge_all_data, calculate_religious_need_score, calculate_missionary_gap_score
from src.visualization.maps import create_choropleth
from src.visualization.tables import format_rankings_dataframe
from src.visualization.charts import (
    create_score_breakdown_chart,
    create_scatter_plot,
)
from src.utils.normalization import min_max_normalize


# Page configuration
st.set_page_config(
    page_title="Mission-Action: Strategic Outreach Opportunities",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(ttl=3600)
def load_base_data():
    """Load merged base data (without computed scores)."""
    merged = merge_all_data()
    if merged.empty:
        st.error("No data available. Please check data files in data/raw/")
        return pd.DataFrame()
    return merged


def calculate_action_sports_score_weighted(
    df: pd.DataFrame,
    tourism_infra_weight: float = 0.40,
    safety_weight: float = 0.30,
    natural_resources_weight: float = 0.30
) -> pd.Series:
    """Calculate Action Sports Score with custom weights.

    Components:
    - Tourism Infrastructure: From TTDI score
    - Safety: Inverse of persecution (countries with less persecution are safer)
    - Natural Resources: Proxy based on continent/region diversity
    """

    # Tourism Infrastructure from TTDI
    if 'ttdi_score' in df.columns:
        ttdi = df['ttdi_score'].fillna(df['ttdi_score'].median())
        tourism_infra = min_max_normalize(
            ttdi,
            min_val=1.0,
            max_val=6.0,
            target_min=0,
            target_max=100
        )
    else:
        tourism_infra = pd.Series([50.0] * len(df), index=df.index)

    # Safety score (inverse of persecution - less persecution = safer for travelers)
    if 'persecution_score' in df.columns:
        # Countries not in WWL get score of 0 (no persecution data = likely safe)
        persecution = df['persecution_score'].fillna(0)
        safety = 100 - persecution  # Invert: high persecution = low safety
    elif 'legal_openness' in df.columns:
        safety = df['legal_openness'].fillna(100)
    else:
        safety = pd.Series([75.0] * len(df), index=df.index)

    # Natural Resources proxy - based on geographic diversity
    # Countries with varied terrain score higher (this is an approximation)
    # Using continent as a rough proxy for now
    natural_resources = pd.Series([60.0] * len(df), index=df.index)
    if 'continent' in df.columns:
        # Boost scores for continents known for adventure sports
        continent_bonuses = {
            'Oceania': 20,
            'Latin America': 15,
            'Africa': 15,
            'Europe': 10,
            'Asia': 10,
            'North America': 10,
        }
        for continent, bonus in continent_bonuses.items():
            mask = df['continent'] == continent
            natural_resources.loc[mask] = 60 + bonus

    # Normalize weights to sum to 1
    total_weight = tourism_infra_weight + safety_weight + natural_resources_weight
    if total_weight > 0:
        tourism_infra_weight /= total_weight
        safety_weight /= total_weight
        natural_resources_weight /= total_weight

    # Calculate weighted score
    action_score = (
        tourism_infra_weight * tourism_infra.clip(0, 100) +
        safety_weight * safety.clip(0, 100) +
        natural_resources_weight * natural_resources.clip(0, 100)
    )

    return action_score.clip(0, 100)


def calculate_outreach_score_weighted(
    df: pd.DataFrame,
    religious_need_weight: float = 0.40,
    missionary_gap_weight: float = 0.25,
    legal_openness_weight: float = 0.35
) -> pd.Series:
    """Calculate Outreach Score with custom weights."""

    # Calculate component scores
    religious_need = calculate_religious_need_score(df)
    missionary_gap = calculate_missionary_gap_score(df)

    # Legal openness (inverse of persecution)
    if 'legal_openness' in df.columns:
        legal_openness = df['legal_openness'].fillna(100)
    elif 'persecution_score' in df.columns:
        legal_openness = 100 - df['persecution_score'].fillna(0)
    else:
        legal_openness = pd.Series([100.0] * len(df), index=df.index)

    # Normalize weights to sum to 1
    total_weight = religious_need_weight + missionary_gap_weight + legal_openness_weight
    if total_weight > 0:
        religious_need_weight /= total_weight
        missionary_gap_weight /= total_weight
        legal_openness_weight /= total_weight

    # Calculate weighted score
    outreach_score = (
        religious_need_weight * religious_need.clip(0, 100) +
        missionary_gap_weight * missionary_gap.clip(0, 100) +
        legal_openness_weight * legal_openness.clip(0, 100)
    )

    return outreach_score.clip(0, 100)


def calculate_combined_score_weighted(
    action_score: pd.Series,
    outreach_score: pd.Series,
    action_weight: float = 0.5,
    outreach_weight: float = 0.5,
    method: str = "multiply"
) -> pd.Series:
    """Calculate combined score with custom weights."""

    if method == "multiply":
        # Multiply and scale back to 0-100
        combined = (action_score * outreach_score) / 100
    elif method == "weighted_average":
        # Normalize weights
        total = action_weight + outreach_weight
        if total > 0:
            action_weight /= total
            outreach_weight /= total
        combined = (action_weight * action_score) + (outreach_weight * outreach_score)
    else:
        combined = (action_score * outreach_score) / 100

    return combined.clip(0, 100)


def generate_rankings_with_weights(
    df: pd.DataFrame,
    action_sports_weights: dict,
    outreach_weights: dict,
    combined_weights: dict,
    combination_method: str = "multiply"
) -> pd.DataFrame:
    """Generate rankings with custom weights."""

    result = df.copy()

    # Calculate Action Sports Score with custom weights
    result['action_sports_score'] = calculate_action_sports_score_weighted(
        result,
        tourism_infra_weight=action_sports_weights.get('tourism_infra', 0.40),
        safety_weight=action_sports_weights.get('safety', 0.30),
        natural_resources_weight=action_sports_weights.get('natural_resources', 0.30)
    )

    # Calculate Outreach Score with custom weights
    result['outreach_score'] = calculate_outreach_score_weighted(
        result,
        religious_need_weight=outreach_weights.get('religious_need', 0.40),
        missionary_gap_weight=outreach_weights.get('missionary_gap', 0.25),
        legal_openness_weight=outreach_weights.get('legal_openness', 0.35)
    )

    # Calculate Combined Score
    result['combined_score'] = calculate_combined_score_weighted(
        result['action_sports_score'],
        result['outreach_score'],
        action_weight=combined_weights.get('action_sports', 0.5),
        outreach_weight=combined_weights.get('outreach', 0.5),
        method=combination_method
    )

    # Generate rankings
    result['action_sports_rank'] = result['action_sports_score'].rank(
        ascending=False, method='min'
    ).astype(int)

    result['outreach_rank'] = result['outreach_score'].rank(
        ascending=False, method='min'
    ).astype(int)

    result['combined_rank'] = result['combined_score'].rank(
        ascending=False, method='min'
    ).astype(int)

    # Round scores
    result['action_sports_score'] = result['action_sports_score'].round(1)
    result['outreach_score'] = result['outreach_score'].round(1)
    result['combined_score'] = result['combined_score'].round(1)

    return result.sort_values('combined_rank')


def get_default_weights():
    """Return default weight values."""
    return {
        'action_sports_weights': {
            'tourism_infra': 0.40,
            'safety': 0.30,
            'natural_resources': 0.30,
        },
        'outreach_weights': {
            'religious_need': 0.40,
            'missionary_gap': 0.25,
            'legal_openness': 0.35,
        },
        'combined_weights': {
            'action_sports': 0.5,
            'outreach': 0.5,
        },
        'combination_method': 'multiply'
    }


def reset_weights_callback():
    """Callback to reset all weights to defaults."""
    defaults = get_default_weights()

    # Set session state to default values
    st.session_state['weight_tourism_infra'] = defaults['action_sports_weights']['tourism_infra']
    st.session_state['weight_safety'] = defaults['action_sports_weights']['safety']
    st.session_state['weight_natural_resources'] = defaults['action_sports_weights']['natural_resources']
    st.session_state['weight_religious_need'] = defaults['outreach_weights']['religious_need']
    st.session_state['weight_missionary_gap'] = defaults['outreach_weights']['missionary_gap']
    st.session_state['weight_legal_openness'] = defaults['outreach_weights']['legal_openness']
    st.session_state['combination_method'] = defaults['combination_method']

    # Reset combined weights if they exist
    if 'weight_action_combined' in st.session_state:
        st.session_state['weight_action_combined'] = defaults['combined_weights']['action_sports']
    if 'weight_outreach_combined' in st.session_state:
        st.session_state['weight_outreach_combined'] = defaults['combined_weights']['outreach']


def render_weight_sidebar():
    """Render the sidebar with weight controls."""

    defaults = get_default_weights()

    st.sidebar.header("Customize Weights")
    st.sidebar.markdown("Adjust the weights to see how rankings change.")

    # Reset button with callback
    st.sidebar.button(
        "Reset to Defaults",
        key="reset_weights",
        type="primary",
        on_click=reset_weights_callback
    )

    st.sidebar.divider()

    # Action Sports Score Weights
    st.sidebar.subheader("Action Sports Score")

    tourism_infra = st.sidebar.slider(
        "Tourism Infrastructure",
        min_value=0.0, max_value=1.0,
        value=defaults['action_sports_weights']['tourism_infra'],
        step=0.05,
        help="Weight for hotels, transport, tourism services (from TTDI)",
        key="weight_tourism_infra"
    )

    safety = st.sidebar.slider(
        "Safety & Accessibility",
        min_value=0.0, max_value=1.0,
        value=defaults['action_sports_weights']['safety'],
        step=0.05,
        help="Weight for traveler safety (inverse of persecution)",
        key="weight_safety"
    )

    natural_resources = st.sidebar.slider(
        "Natural Resources",
        min_value=0.0, max_value=1.0,
        value=defaults['action_sports_weights']['natural_resources'],
        step=0.05,
        help="Weight for terrain diversity and adventure potential",
        key="weight_natural_resources"
    )

    # Show normalized weights
    total_action = tourism_infra + safety + natural_resources
    if total_action > 0:
        st.sidebar.caption(
            f"Normalized: Infra {tourism_infra/total_action:.0%}, "
            f"Safety {safety/total_action:.0%}, "
            f"Nature {natural_resources/total_action:.0%}"
        )

    st.sidebar.divider()

    # Outreach Score Weights
    st.sidebar.subheader("Outreach Score")

    religious_need = st.sidebar.slider(
        "Religious Need",
        min_value=0.0, max_value=1.0,
        value=defaults['outreach_weights']['religious_need'],
        step=0.05,
        help="Weight for % non-Christian and unreached populations",
        key="weight_religious_need"
    )

    missionary_gap = st.sidebar.slider(
        "Missionary Gap",
        min_value=0.0, max_value=1.0,
        value=defaults['outreach_weights']['missionary_gap'],
        step=0.05,
        help="Weight for current missionary engagement vs. need",
        key="weight_missionary_gap"
    )

    legal_openness = st.sidebar.slider(
        "Legal Openness",
        min_value=0.0, max_value=1.0,
        value=defaults['outreach_weights']['legal_openness'],
        step=0.05,
        help="Weight for religious freedom (inverse of persecution)",
        key="weight_legal_openness"
    )

    # Show normalized weights
    total_outreach = religious_need + missionary_gap + legal_openness
    if total_outreach > 0:
        st.sidebar.caption(
            f"Normalized: Need {religious_need/total_outreach:.0%}, "
            f"Gap {missionary_gap/total_outreach:.0%}, "
            f"Open {legal_openness/total_outreach:.0%}"
        )

    st.sidebar.divider()

    # Combined Score Settings
    st.sidebar.subheader("Combined Score")

    combination_method = st.sidebar.radio(
        "Combination Method",
        options=["multiply", "weighted_average"],
        format_func=lambda x: "Multiply (A × O / 100)" if x == "multiply" else "Weighted Average",
        help="How to combine Action Sports and Outreach scores",
        key="combination_method"
    )

    action_weight = 0.5
    outreach_weight = 0.5

    if combination_method == "weighted_average":
        action_weight = st.sidebar.slider(
            "Action Sports Weight",
            min_value=0.0, max_value=1.0, value=0.5, step=0.05,
            key="weight_action_combined"
        )
        outreach_weight = st.sidebar.slider(
            "Outreach Weight",
            min_value=0.0, max_value=1.0, value=0.5, step=0.05,
            key="weight_outreach_combined"
        )

        total_combined = action_weight + outreach_weight
        if total_combined > 0:
            st.sidebar.caption(
                f"Normalized: Action {action_weight/total_combined:.0%}, "
                f"Outreach {outreach_weight/total_combined:.0%}"
            )

    return {
        'action_sports_weights': {
            'tourism_infra': tourism_infra,
            'safety': safety,
            'natural_resources': natural_resources,
        },
        'outreach_weights': {
            'religious_need': religious_need,
            'missionary_gap': missionary_gap,
            'legal_openness': legal_openness,
        },
        'combined_weights': {
            'action_sports': action_weight,
            'outreach': outreach_weight,
        },
        'combination_method': combination_method
    }


def get_top_countries(df: pd.DataFrame, score_type: str = "combined", top_n: int = 10) -> pd.DataFrame:
    """Get top N countries for a given score type."""
    rank_col = f"{score_type}_rank"
    if rank_col not in df.columns:
        return df.head(top_n)
    return df.nsmallest(top_n, rank_col)


def get_country_details(df: pd.DataFrame, country_name: str) -> dict:
    """Get detailed information for a specific country."""
    country_row = df[df['country_name'] == country_name]

    if country_row.empty:
        country_row = df[df['Country'] == country_name]

    if country_row.empty:
        return None

    row = country_row.iloc[0]

    return {
        'name': row.get('country_name', row.get('Country', country_name)),
        'iso_code': row.get('iso_alpha_3', ''),
        'continent': row.get('continent', ''),
        'population': row.get('population', 0),
        'primary_religion': row.get('primary_religion', ''),
        'scores': {
            'action_sports': row.get('action_sports_score', 0),
            'outreach': row.get('outreach_score', 0),
            'combined': row.get('combined_score', 0),
        },
        'ranks': {
            'action_sports': row.get('action_sports_rank', 0),
            'outreach': row.get('outreach_rank', 0),
            'combined': row.get('combined_rank', 0),
        },
        'components': {
            'pct_christian': row.get('pct_christian', 0),
            'pct_evangelical': row.get('pct_evangelical', 0),
            'pct_unreached': row.get('pct_unreached', 0),
            'unreached_groups': row.get('unreached_groups', 0),
            'persecution_score': row.get('persecution_score', 0),
            'legal_openness': row.get('legal_openness', 100),
            'ttdi_score': row.get('ttdi_score', 0),
        }
    }


def render_header():
    """Render the page header."""
    st.title("Mission-Action")
    st.markdown("""
    **Combining Extreme Sports Potential and Christian Outreach Opportunities by Country**

    This platform identifies countries where adventure tourism and outreach potential align.
    *Use the sidebar to customize weights and see rankings update in real-time.*
    """)

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

        search = st.text_input(
            "Search countries",
            placeholder="Type to search...",
            key=f"search_{score_type}"
        )

        filtered_df = df.copy()
        if search:
            name_col = 'country_name' if 'country_name' in df.columns else 'Country'
            filtered_df = df[
                df[name_col].str.lower().str.contains(search.lower(), na=False)
            ]

        display_cols = ['country_name', f'{score_type}_rank', f'{score_type}_score']
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

    st.markdown("### Score Breakdown")
    fig = create_score_breakdown_chart(details, chart_type='bar')
    st.plotly_chart(fig, use_container_width=True, key="country_detail_chart")


def render_methodology(weights: dict):
    """Render the methodology section."""
    st.markdown("## Methodology")

    action_w = weights['action_sports_weights']
    total_a = sum(action_w.values())
    outreach_w = weights['outreach_weights']
    total_o = sum(outreach_w.values())

    with st.expander("Scoring Methodology", expanded=False):
        st.markdown(f"""
        ### Action Sports Score (0-100)

        *Current weights (adjustable in sidebar):*
        - **Tourism Infrastructure** ({action_w['tourism_infra']/total_a*100:.0f}%) - Hotels, transport, services (from TTDI)
        - **Safety & Accessibility** ({action_w['safety']/total_a*100:.0f}%) - Traveler safety, political stability
        - **Natural Resources** ({action_w['natural_resources']/total_a*100:.0f}%) - Terrain diversity, adventure potential

        ### Christian Outreach Score (0-100)

        *Current weights (adjustable in sidebar):*
        - **Religious Demographics** ({outreach_w['religious_need']/total_o*100:.0f}%) - % non-Christian, unreached populations
        - **Missionary Gap** ({outreach_w['missionary_gap']/total_o*100:.0f}%) - Current engagement vs. need
        - **Legal Openness** ({outreach_w['legal_openness']/total_o*100:.0f}%) - Religious freedom, inverse of persecution

        ### Combined Score

        Method: **{weights['combination_method'].replace('_', ' ').title()}**

        {"Multiplies Action Sports × Outreach, divided by 100." if weights['combination_method'] == 'multiply' else 'Weighted average of both scores.'}
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
    st.plotly_chart(fig, use_container_width=True, key="scatter_analysis")

    st.markdown("""
    *Countries in the upper-right quadrant have both high action sports
    potential AND high outreach opportunity — these are prime targets for
    mission work through adventure sports.*
    """)


def main():
    """Main application entry point."""

    # Load base data
    base_df = load_base_data()

    if base_df.empty:
        st.error("Unable to load data. Please ensure data files exist in data/raw/")
        return

    # Render sidebar with weight controls
    weights = render_weight_sidebar()

    # Calculate rankings with current weights
    df = generate_rankings_with_weights(
        base_df,
        action_sports_weights=weights['action_sports_weights'],
        outreach_weights=weights['outreach_weights'],
        combined_weights=weights['combined_weights'],
        combination_method=weights['combination_method']
    )

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

        st.divider()
        name_col = 'country_name' if 'country_name' in df.columns else 'Country'
        countries = sorted(df[name_col].dropna().unique())
        selected = st.selectbox("Select a country for details:", [""] + list(countries), key="country_select")
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

        st.subheader("Scores by Continent")
        if 'continent' in df.columns:
            continent_avg = df.groupby('continent').agg({
                'action_sports_score': 'mean',
                'outreach_score': 'mean',
                'combined_score': 'mean',
            }).round(1)
            st.dataframe(continent_avg, use_container_width=True, key="continent_table")

    with tab_methodology:
        render_methodology(weights)

    # Footer
    st.divider()
    st.markdown("""
    ---
    *Data sources: Joshua Project, Open Doors, WEF TTDI 2024, Pew Research*

    **Mission-Action** | Connecting Adventure Sports with Strategic Outreach
    """)


if __name__ == "__main__":
    main()
