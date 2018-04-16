import numpy as np

from bokeh.models import Tabs, Panel
from bokeh.plotting import Figure
from typing import List, Union

from pyesg.validation.report.analysis_builders.base.base_builder import BaseBuilder
from pyesg.validation.report.charts.line_chart import LineChart
from pyesg.validation.report.charts.moment_chart import MomentChart


class MomentAnalysisBuilder(BaseBuilder):
    """
    Base class for building the charts for a moment analysis.
    """
    title = None

    def perform_additional_formatting(self, moment: str, charter: LineChart,
                                      min_x_value: float = None, max_x_value: float = None,
                                      min_y_value: float = None, max_y_value: float = None) -> None:
        """
        Performs any specific additional formatting on the chart
        Args:
            moment: The moment that the chart is plotting.
            charter: The charter class used for creating the plot.
            min_x_value: The minimum x value in the plot.
            max_x_value: The maximum x value in the plot.
            min_y_value: The minimum y value in the plot.
            max_y_value: The maximum y value in the plot.
        """
        pass

    def build_chart(self, results: dict) -> Union[Figure, List[Figure], Tabs]:
        """
        Returns the figure to include in the report for a moments analysis
        Args:
            results: The results of the moment analysis. It should contain keys:
                'time', 'mean', 'volatility', 'skewness' and 'kurtosis'

        Returns:
            The figure to include in the report for a moments analysis.

        This returns 4 tabs of graphs - one for each moment.
        """
        if not self.title:
            raise ValueError("No title for the chart for a martingale analysis.")

        moments = ['mean', 'volatility', 'skewness', 'kurtosis']
        panels = []
        for moment in moments:
            charter = MomentChart(title=self.title, x_axis_label="Time (y)")
            charter.plot_from_results(results=results, moment=moment)
            x_values = results["time"]
            y_values = results[moment]
            self.perform_additional_formatting(moment, charter,
                                               min_x_value=np.min(x_values), max_x_value=np.max(x_values),
                                               min_y_value=np.min(y_values), max_y_value=np.max(y_values)
                                               )
            panel = Panel(child=charter.figure, title=moment.capitalize())
            panels.append(panel)

        return Tabs(tabs=panels)
