"""Score normalization utilities for scaling values to 0-100 range."""

import numpy as np
import pandas as pd
from typing import Union, Optional


def min_max_normalize(
    values: Union[pd.Series, np.ndarray, list],
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
    target_min: float = 0,
    target_max: float = 100,
    invert: bool = False
) -> pd.Series:
    """Normalize values to a target range using min-max scaling.

    Args:
        values: Input values to normalize
        min_val: Minimum value for scaling (uses data min if None)
        max_val: Maximum value for scaling (uses data max if None)
        target_min: Target minimum value (default 0)
        target_max: Target maximum value (default 100)
        invert: If True, invert the scale (high becomes low)

    Returns:
        Normalized pandas Series
    """
    series = pd.Series(values)

    if min_val is None:
        min_val = series.min()
    if max_val is None:
        max_val = series.max()

    # Avoid division by zero
    if max_val == min_val:
        return pd.Series([target_max] * len(series))

    # Normalize to 0-1 range
    normalized = (series - min_val) / (max_val - min_val)

    # Invert if requested
    if invert:
        normalized = 1 - normalized

    # Scale to target range
    scaled = normalized * (target_max - target_min) + target_min

    # Clip to target range
    return scaled.clip(target_min, target_max)


def percentile_normalize(
    values: Union[pd.Series, np.ndarray, list],
    target_min: float = 0,
    target_max: float = 100
) -> pd.Series:
    """Normalize values based on their percentile rank.

    Args:
        values: Input values to normalize
        target_min: Target minimum value (default 0)
        target_max: Target maximum value (default 100)

    Returns:
        Normalized pandas Series
    """
    series = pd.Series(values)

    # Calculate percentile ranks (0-1)
    ranks = series.rank(pct=True, na_option='keep')

    # Scale to target range
    scaled = ranks * (target_max - target_min) + target_min

    return scaled


def z_score_normalize(
    values: Union[pd.Series, np.ndarray, list],
    target_mean: float = 50,
    target_std: float = 15
) -> pd.Series:
    """Normalize values using z-score transformation.

    Args:
        values: Input values to normalize
        target_mean: Target mean (default 50)
        target_std: Target standard deviation (default 15)

    Returns:
        Normalized pandas Series
    """
    series = pd.Series(values)

    mean = series.mean()
    std = series.std()

    if std == 0:
        return pd.Series([target_mean] * len(series))

    # Calculate z-scores
    z_scores = (series - mean) / std

    # Transform to target distribution
    normalized = z_scores * target_std + target_mean

    return normalized


def combine_weighted_scores(
    scores: dict,
    weights: dict,
    normalize_output: bool = True
) -> pd.Series:
    """Combine multiple score series with weights.

    Args:
        scores: Dict mapping score names to pandas Series
        weights: Dict mapping score names to weights (should sum to 1.0)
        normalize_output: Whether to normalize the final output to 0-100

    Returns:
        Combined weighted score as pandas Series
    """
    # Validate weights
    total_weight = sum(weights.values())
    if abs(total_weight - 1.0) > 0.01:
        # Normalize weights
        weights = {k: v / total_weight for k, v in weights.items()}

    # Calculate weighted sum
    combined = pd.Series(0.0, index=next(iter(scores.values())).index)

    for name, series in scores.items():
        weight = weights.get(name, 0)
        combined = combined + (series * weight)

    if normalize_output:
        combined = min_max_normalize(combined, target_min=0, target_max=100)

    return combined


def calculate_combined_score(
    score_a: pd.Series,
    score_b: pd.Series,
    method: str = "multiply"
) -> pd.Series:
    """Calculate combined score from two input scores.

    Args:
        score_a: First score series (0-100)
        score_b: Second score series (0-100)
        method: Combination method ("multiply", "average", "geometric_mean")

    Returns:
        Combined score as pandas Series (0-100)
    """
    if method == "multiply":
        # Multiply and scale back to 0-100
        combined = (score_a * score_b) / 100
    elif method == "average":
        combined = (score_a + score_b) / 2
    elif method == "geometric_mean":
        combined = np.sqrt(score_a * score_b)
    else:
        raise ValueError(f"Unknown method: {method}")

    return combined.clip(0, 100)
