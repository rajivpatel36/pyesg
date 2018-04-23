from bokeh.models import Tabs, Panel, NumeralTickFormatter
from bokeh.plotting import Figure
from typing import List, Union

from pyesg.validation.report.analysis_builders.base.base_builder import BaseBuilder
from pyesg.validation.report.charts.martingale_chart import MartingaleChart


class DiscountedZCBBuilder(BaseBuilder):
    """
    Class for building the charts for a discounted ZCB analysis.
    """
    title = "Discounted Zero Coupon Bond"

    def build_chart(self, results: List) -> Union[Figure, List[Figure], Tabs]:
        """
        Returns the figure to include in the report for a discounted ZCB analysis
        Args:
            results: The results of the discounted ZCB analysis. It is a list of dicts containing the results
                     for each ZCB term that has been included in the analysis.

        Returns:
            The figure to include in the report for the discounted ZCB analysis.

        This returns tabs of graphs - one for each ZCB term that is included.
        """
        panels = []
        for term_result in results:
            term = term_result["term"]
            charter = MartingaleChart(title=self.title, x_axis_label="Time (y)", y_axis_label="Spot rate")
            charter.plot_from_results(results=term_result, sample_mean_name=f"Discounted ZCB ({term}y)")
            charter._figure.yaxis[0].formatter = NumeralTickFormatter(format="0.00%")
            panel = Panel(child=charter.figure, title=f"ZCB ({term}y)")
            panels.append(panel)

        return Tabs(tabs=panels)
