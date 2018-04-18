from pyesg.constants.validation_analyses import *
from pyesg.validation.report.analysis_builders.average_discount_factor_builder import AverageDiscountFactorBuilder
from pyesg.validation.report.analysis_builders.base.base_builder import BaseBuilder
from pyesg.validation.report.analysis_builders.discounted_tri_builder import DiscountedTRIBuilder
from pyesg.validation.report.analysis_builders.tri_log_return_moments_builder import TRILogReturnMomentsBuilder

BUILDERS = {
    AVERAGE_DISCOUNT_FACTOR: AverageDiscountFactorBuilder,
    DISCOUNTED_TOTAL_RETURN_INDEX: DiscountedTRIBuilder,
    TOTAL_RETURN_INDEX_LOG_RETURN_MOMENTS: TRILogReturnMomentsBuilder,
}


def get_analysis_builder(analysis_id: str) -> BaseBuilder:
    """
    Returns an analysis builder for an analysis with the specified id which can be used to build the charts
    for the analysis to include in the report.
    Args:
        analysis_id: The id for the analysis.

    Returns:
        An instance of the analysis builder class for the analysis corresponding to the specified id.
    """
    cls = BUILDERS.get(analysis_id)
    if not cls:
        raise ValueError(f"Validation analysis {analysis_id} not supported.")

    return cls()
