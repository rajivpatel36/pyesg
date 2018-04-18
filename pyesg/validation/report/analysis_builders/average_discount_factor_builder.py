from bokeh.models import NumeralTickFormatter

from pyesg.validation.report.analysis_builders.base.martingale_analysis_builder import MartingaleAnalysisBuilder
from pyesg.validation.report.charts.line_chart import LineChart


class AverageDiscountFactorBuilder(MartingaleAnalysisBuilder):
    """
    Class for building the charts for a discounted TRI analysis.
    """
    title = "Average discount factor"
    y_axis_label = "Spot rate"

    def perform_additional_formatting(self, charter: LineChart):
        # Format y-axis labels as %s
        charter._figure.yaxis[0].formatter = NumeralTickFormatter(format="0.00%")
