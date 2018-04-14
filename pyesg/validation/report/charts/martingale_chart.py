from bokeh.models import ColumnDataSource
from typing import Dict, List

from pyesg.validation.report.charts.line_chart import LineChart


class MartingaleChart(LineChart):
    def plot_from_results(self, results: Dict[str, List[float]], sample_mean_name: str = None) -> None:
        """
        Plots results of a martingale analysis on a line chart.
        Args:
            results: The results of the martingale analysis. It should contain keys:
                'time', 'lower_confidence_interval', 'upper_confidence_interval', 'sample_mean', 'expected_value'
            sample_mean_name: The name of the quantity for which the sample mean is calculated in the analysis.
        """
        data = ColumnDataSource(dict(
            time=results['time'],
            lower_ci=results['lower_confidence_interval'],
            upper_ci=results['upper_confidence_interval'],
            mean=results['sample_mean'],
            expected=results['expected_value'],
        ))
        ys = [
            dict(y='mean', color='black', legend=sample_mean_name or "Sample mean"),
            dict(y='upper_ci', color='red', legend="Upper CI"),
            dict(y='lower_ci', color='red', legend="Lower CI"),
            dict(y='expected', color='blue', legend="Expected value", line_dash='dashed')
        ]
        self.plot(
            data_source=data,
            x='time',
            ys=ys,
            muted_alpha = 0.2  # Muting of line when hidden by clicking on series in legend
        )
