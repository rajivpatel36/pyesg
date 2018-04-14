from pyesg.validation.report.analysis_builders.base.martingale_analysis_builder import MartingaleAnalysisBuilder
from pyesg.validation.report.charts.line_chart import LineChart


class DiscountedTRIBuilder(MartingaleAnalysisBuilder):
    """
    Class for building the charts for a discounted TRI analysis.
    """
    title = "Discounted TRI"

    def perform_additional_formatting(self, charter: LineChart):
        # Adjust y-axis:w
        charter.set_y_range(0.8, 1.2)
