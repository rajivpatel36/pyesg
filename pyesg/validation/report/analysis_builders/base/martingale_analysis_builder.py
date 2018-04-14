from bokeh.models import Tabs
from bokeh.plotting import Figure
from typing import List, Union

from pyesg.validation.report.analysis_builders.base.base_builder import BaseBuilder
from pyesg.validation.report.charts.line_chart import LineChart
from pyesg.validation.report.charts.martingale_chart import MartingaleChart


class MartingaleAnalysisBuilder(BaseBuilder):
    """
    Base class for building the charts for a martingale analysis.
    """
    title = None

    def perform_additional_formatting(self, charter: LineChart) -> None:
        """
        Performs any specific additional formatting on the chart
        Args:
            charter: The charter class used for creating the plot.
        """
        pass

    def build_chart(self, results: dict) -> Union[Figure, List[Figure], Tabs]:
        """
        Returns the figure to include in the report for a martingale anlaysis
        Args:
            results: The results of the martingale analysis. It should contain keys:
                'time', 'lower_confidence_interval', 'upper_confidence_interval', 'sample_mean', 'expected_value'

        Returns:
            The figure to include in the report for a martingale analysis.
        """
        if not self.title:
            raise ValueError("No title for the chart for a martingale analysis.")
        charter = MartingaleChart(title=self.title, x_axis_label="Time (y)")
        charter.plot_from_results(results=results, sample_mean_name=self.title)
        self.perform_additional_formatting(charter)
        return charter.figure
