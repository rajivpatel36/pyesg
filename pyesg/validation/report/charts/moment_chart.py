from bokeh.models import ColumnDataSource
from typing import Dict, List

from pyesg.validation.report.charts.line_chart import LineChart


class MomentChart(LineChart):
    def plot_from_results(self, results: Dict[str, List[float]], moment: str) -> None:
        """
        Plots results of a moment analysis on a line chart.
        Args:
            results: The results of the moment analysis. It should contain keys:
                'time', 'mean', 'volatility', 'skewness', 'kurtosis'
            moment: The moment to plot. This is either 'mean', 'volatilit', 'skewness' or 'kurtosis'
        """
        data = ColumnDataSource(dict(
            time=results['time'],
            moment=results[moment],
        ))
        ys = [dict(y='moment', legend=moment.capitalize())]

        self.plot(
            data_source=data,
            x='time',
            ys=ys,
            color='black',
        )
