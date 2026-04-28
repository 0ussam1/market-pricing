from dataclasses import dataclass


@dataclass
class PipelineResult:
    stats: dict
    best_deal_id: int | None
    analysis_results: list
    association_rules: list
    pca_points: list


def run_mining_pipeline(raw_prices):
    """Run the full mining pipeline on scraped prices. Stub — will be implemented in a dedicated task."""
    return PipelineResult(
        stats={},
        best_deal_id=None,
        analysis_results=[],
        association_rules=[],
        pca_points=[],
    )
