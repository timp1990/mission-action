"""Christian Outreach Opportunity Score calculator."""

import pandas as pd
from dataclasses import dataclass

from src.utils.normalization import min_max_normalize
from src.data.processors import calculate_religious_need_score, calculate_missionary_gap_score


@dataclass
class OutreachWeights:
    """Weights for Outreach Score components.

    All weights should sum to 1.0.
    """
    religious_need: float = 0.40  # Religious demographics (% non-Christian, unreached)
    missionary_gap: float = 0.25  # Gap in missionary engagement
    legal_openness: float = 0.35  # Legal freedom for Christianity

    def validate(self) -> bool:
        """Validate that weights sum to 1.0."""
        total = self.religious_need + self.missionary_gap + self.legal_openness
        return abs(total - 1.0) < 0.01


class OutreachScorer:
    """Calculate Christian Outreach Opportunity Score for countries.

    The Outreach Score represents the opportunity and need for
    Christian outreach in a country, based on:
    - Religious demographics (% non-Christian, unreached populations)
    - Missionary presence/engagement gap
    - Legal openness (inverse of persecution)

    A high score indicates both high need AND reasonable openness
    for outreach activities.
    """

    def __init__(self, weights: OutreachWeights = None):
        """Initialize scorer with optional custom weights.

        Args:
            weights: Custom weights for score components
        """
        self.weights = weights or OutreachWeights()

    def calculate(self, df: pd.DataFrame) -> pd.Series:
        """Calculate Outreach Score for all countries.

        Args:
            df: DataFrame with required columns:
                - pct_christian
                - pct_unreached
                - unreached_groups
                - pct_evangelical
                - legal_openness (or persecution_score)

        Returns:
            Series with Outreach Scores (0-100)
        """
        # Calculate component scores
        religious_need = calculate_religious_need_score(df)
        missionary_gap = calculate_missionary_gap_score(df)

        # Legal openness (inverse of persecution)
        if 'legal_openness' in df.columns:
            legal_openness = df['legal_openness'].fillna(100)  # Default to fully open
        elif 'persecution_score' in df.columns:
            legal_openness = 100 - df['persecution_score'].fillna(0)
        else:
            legal_openness = pd.Series([100.0] * len(df), index=df.index)

        # Ensure all scores are 0-100
        religious_need = religious_need.clip(0, 100)
        missionary_gap = missionary_gap.clip(0, 100)
        legal_openness = legal_openness.clip(0, 100)

        # Calculate weighted score
        outreach_score = (
            self.weights.religious_need * religious_need +
            self.weights.missionary_gap * missionary_gap +
            self.weights.legal_openness * legal_openness
        )

        return outreach_score.clip(0, 100)

    def get_component_breakdown(self, df: pd.DataFrame) -> pd.DataFrame:
        """Get detailed component breakdown for each country.

        Args:
            df: DataFrame with required columns

        Returns:
            DataFrame with component scores
        """
        breakdown = pd.DataFrame(index=df.index)

        breakdown['religious_need'] = calculate_religious_need_score(df)
        breakdown['missionary_gap'] = calculate_missionary_gap_score(df)

        if 'legal_openness' in df.columns:
            breakdown['legal_openness'] = df['legal_openness'].fillna(100)
        elif 'persecution_score' in df.columns:
            breakdown['legal_openness'] = 100 - df['persecution_score'].fillna(0)
        else:
            breakdown['legal_openness'] = 100.0

        breakdown['outreach_score'] = self.calculate(df)

        return breakdown


def calculate_outreach_score(df: pd.DataFrame) -> pd.Series:
    """Convenience function to calculate Outreach Score.

    Args:
        df: DataFrame with required columns

    Returns:
        Series with Outreach Scores (0-100)
    """
    scorer = OutreachScorer()
    return scorer.calculate(df)
