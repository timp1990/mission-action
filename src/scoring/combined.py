"""Combined ranking logic for Action Sports and Outreach scores."""

import pandas as pd
import numpy as np

from src.scoring.action_sports import ActionSportsScorer, calculate_action_sports_score
from src.scoring.outreach import OutreachScorer, calculate_outreach_score
from src.data.processors import merge_all_data
from src.data.loaders import save_processed_data


def calculate_combined_score(
    action_score: pd.Series,
    outreach_score: pd.Series,
    method: str = "multiply"
) -> pd.Series:
    """Calculate combined score from Action Sports and Outreach scores.

    Args:
        action_score: Action Sports scores (0-100)
        outreach_score: Outreach scores (0-100)
        method: Combination method:
            - "multiply": Multiply and normalize to 0-100
            - "average": Simple average
            - "geometric_mean": Geometric mean

    Returns:
        Combined scores (0-100)
    """
    if method == "multiply":
        # Multiply and scale back to 0-100
        # (A * B) / 100 where A,B are 0-100
        combined = (action_score * outreach_score) / 100
    elif method == "average":
        combined = (action_score + outreach_score) / 2
    elif method == "geometric_mean":
        combined = np.sqrt(action_score * outreach_score)
    else:
        raise ValueError(f"Unknown combination method: {method}")

    return combined.clip(0, 100)


def generate_rankings(df: pd.DataFrame) -> pd.DataFrame:
    """Generate complete rankings with all scores.

    Args:
        df: Merged DataFrame with all source data

    Returns:
        DataFrame with scores and rankings
    """
    result = df.copy()

    # Calculate individual scores
    result['action_sports_score'] = calculate_action_sports_score(result)
    result['outreach_score'] = calculate_outreach_score(result)

    # Calculate combined score
    result['combined_score'] = calculate_combined_score(
        result['action_sports_score'],
        result['outreach_score'],
        method="multiply"
    )

    # Generate rankings (higher score = better rank = lower number)
    result['action_sports_rank'] = result['action_sports_score'].rank(
        ascending=False, method='min'
    ).astype(int)

    result['outreach_rank'] = result['outreach_score'].rank(
        ascending=False, method='min'
    ).astype(int)

    result['combined_rank'] = result['combined_score'].rank(
        ascending=False, method='min'
    ).astype(int)

    # Round scores to 1 decimal place
    result['action_sports_score'] = result['action_sports_score'].round(1)
    result['outreach_score'] = result['outreach_score'].round(1)
    result['combined_score'] = result['combined_score'].round(1)

    # Sort by combined rank
    result = result.sort_values('combined_rank')

    return result


def get_component_breakdowns(df: pd.DataFrame) -> dict:
    """Get detailed component breakdowns for all scoring dimensions.

    Args:
        df: Merged DataFrame with all source data

    Returns:
        Dict with 'action_sports' and 'outreach' breakdown DataFrames
    """
    action_scorer = ActionSportsScorer()
    outreach_scorer = OutreachScorer()

    return {
        'action_sports': action_scorer.get_component_breakdown(df),
        'outreach': outreach_scorer.get_component_breakdown(df)
    }


def build_and_save_rankings() -> pd.DataFrame:
    """Build complete rankings and save to processed data.

    Returns:
        DataFrame with complete rankings
    """
    # Merge all data sources
    merged_df = merge_all_data()

    # Generate rankings
    rankings = generate_rankings(merged_df)

    # Save to processed directory
    save_processed_data(rankings, "combined_rankings.parquet")

    return rankings


def get_top_countries(
    df: pd.DataFrame,
    score_type: str = "combined",
    top_n: int = 10
) -> pd.DataFrame:
    """Get top N countries for a given score type.

    Args:
        df: Rankings DataFrame
        score_type: "combined", "action_sports", or "outreach"
        top_n: Number of top countries to return

    Returns:
        DataFrame with top N countries
    """
    rank_col = f"{score_type}_rank"

    if rank_col not in df.columns:
        raise ValueError(f"Unknown score type: {score_type}")

    return df.nsmallest(top_n, rank_col)


def get_country_details(df: pd.DataFrame, country_name: str) -> dict:
    """Get detailed information for a specific country.

    Args:
        df: Rankings DataFrame
        country_name: Name of the country

    Returns:
        Dict with country details and scores
    """
    # Find country row
    country_row = df[df['country_name'] == country_name]

    if country_row.empty:
        # Try matching on original Country column
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
