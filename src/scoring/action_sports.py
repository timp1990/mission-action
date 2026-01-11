"""Action Sports Score calculator based on adventure tourism metrics."""

import pandas as pd
from dataclasses import dataclass

from src.utils.normalization import min_max_normalize


@dataclass
class ActionSportsWeights:
    """Weights for Action Sports Score components.

    All weights should sum to 1.0.
    """
    ttdi_score: float = 1.0  # Using TTDI as primary indicator

    def validate(self) -> bool:
        """Validate that weights sum to 1.0."""
        total = self.ttdi_score
        return abs(total - 1.0) < 0.01


class ActionSportsScorer:
    """Calculate Action Sports Score for countries.

    The Action Sports Score represents a country's potential for
    extreme sports tourism, based on:
    - Natural and adventure resources
    - Safety and accessibility
    - Tourism infrastructure
    - Sustainability and reputation

    Currently uses WEF TTDI score as a composite indicator that
    captures these dimensions.
    """

    def __init__(self, weights: ActionSportsWeights = None):
        """Initialize scorer with optional custom weights.

        Args:
            weights: Custom weights for score components
        """
        self.weights = weights or ActionSportsWeights()

    def calculate(self, df: pd.DataFrame) -> pd.Series:
        """Calculate Action Sports Score for all countries.

        Args:
            df: DataFrame with ttdi_score column

        Returns:
            Series with Action Sports Scores (0-100)
        """
        if 'ttdi_score' not in df.columns:
            # Return default middle score if no TTDI data
            return pd.Series([50.0] * len(df), index=df.index)

        # TTDI scores are typically 1-6 scale
        # Normalize to 0-100 scale
        ttdi = df['ttdi_score'].fillna(df['ttdi_score'].median())

        # Normalize using actual min/max from data
        action_score = min_max_normalize(
            ttdi,
            min_val=1.0,  # TTDI theoretical minimum
            max_val=6.0,  # TTDI theoretical maximum
            target_min=0,
            target_max=100
        )

        return action_score

    def get_component_breakdown(self, df: pd.DataFrame) -> pd.DataFrame:
        """Get detailed component breakdown for each country.

        Args:
            df: DataFrame with TTDI data

        Returns:
            DataFrame with component scores
        """
        breakdown = pd.DataFrame(index=df.index)

        if 'ttdi_score' in df.columns:
            breakdown['ttdi_raw'] = df['ttdi_score']
            breakdown['ttdi_normalized'] = min_max_normalize(
                df['ttdi_score'].fillna(df['ttdi_score'].median()),
                min_val=1.0,
                max_val=6.0,
                target_min=0,
                target_max=100
            )

        breakdown['action_sports_score'] = self.calculate(df)

        return breakdown


def calculate_action_sports_score(df: pd.DataFrame) -> pd.Series:
    """Convenience function to calculate Action Sports Score.

    Args:
        df: DataFrame with required columns

    Returns:
        Series with Action Sports Scores (0-100)
    """
    scorer = ActionSportsScorer()
    return scorer.calculate(df)
