"""
Annual data refresh script.

Run this script to rebuild the processed data from raw sources.
Execute from the project root directory:
    python scripts/refresh_data.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data.processors import merge_all_data
from src.data.loaders import save_processed_data
from src.scoring.combined import generate_rankings


def main():
    """Rebuild processed data from raw sources."""
    print("=" * 60)
    print("Mission-Action Data Refresh")
    print("=" * 60)

    # Step 1: Merge all data sources
    print("\n[1/3] Merging data sources...")
    merged_df = merge_all_data()

    if merged_df.empty:
        print("ERROR: No data could be merged. Check raw data files.")
        return 1

    print(f"      Merged {len(merged_df)} countries")

    # Step 2: Generate rankings
    print("\n[2/3] Generating rankings...")
    rankings_df = generate_rankings(merged_df)
    print(f"      Computed scores and rankings")

    # Step 3: Save processed data
    print("\n[3/3] Saving processed data...")
    save_processed_data(rankings_df, "combined_rankings.parquet")
    print(f"      Saved to data/processed/combined_rankings.parquet")

    # Summary
    print("\n" + "=" * 60)
    print("Refresh complete!")
    print("=" * 60)

    # Show top 10 combined rankings
    print("\nTop 10 Combined Rankings:")
    print("-" * 40)

    top_10 = rankings_df.nsmallest(10, 'combined_rank')
    for i, (_, row) in enumerate(top_10.iterrows(), 1):
        name = row.get('country_name', row.get('Country', 'Unknown'))
        score = row.get('combined_score', 0)
        print(f"  {i:2d}. {name:25s} {score:.1f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
