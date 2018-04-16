from pyesg.validation.report.analysis_builders.base.moment_analysis_builder import MomentAnalysisBuilder
from pyesg.validation.report.charts.line_chart import LineChart


class TRILogReturnMomentsBuilder(MomentAnalysisBuilder):
    """
    Class for building the charts for a TRI log return moments analysis.
    """
    title = "TRI log return moments"

    def perform_additional_formatting(self, moment: str, charter: LineChart,
                                      min_x_value: float = None, max_x_value: float = None,
                                      min_y_value: float = None, max_y_value: float = None):
        if moment == 'volatility':
            if max_y_value is not None:
                max_y_value *= 1.5
            charter.set_y_range(0, max_y_value)