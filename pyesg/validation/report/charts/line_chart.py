from copy import copy
from typing import List, Union
from bokeh.models import ColumnDataSource, HoverTool, Legend

from bokeh.plotting.helpers import _get_range

from pyesg.validation.report.charts.base_chart import BaseChart


class LineChart(BaseChart):
    """
    Used to create figures for line chart plots.
    """
    def set_x_range(self, lower_limit: Union[float, int], upper_limit: Union[float, int]) -> None:
        """
        Sets the range for the x-axis of the chart.
        Args:
            lower_limit: The lower limit for the axis.
            upper_limit: The upper limit for the axis
        """
        self._figure.x_range = _get_range([lower_limit, upper_limit])

    def set_y_range(self, lower_limit: Union[float, int], upper_limit: Union[float, int]) -> None:
        """
        Sets the range for the y-axis of the chart.
        Args:
            lower_limit: The lower limit for the axis.
            upper_limit: The upper limit for the axis
        """
        self._figure.y_range = _get_range([lower_limit, upper_limit])

    def plot(self, data_source: ColumnDataSource, x: str, ys: List[dict], **kwargs) -> None:
        """
        Plots line charts on a single axis.
        Args:
            data_source: A ColumnDataSource object containing the raw data for the charts.
            x: The name of the column in `data_source` referring to the x-axis values.
            ys: A list containing information about the y-values for each series on the line chart.
                As a minimum each entry should be:
                    {'y': 'name_of_column'}
                where the value of 'y' is the name of the column in `data_source` referring to y-axis values.
                Other keys can be supplied to specify other details about the series. e.g.:
                    - 'color': hex format (#000000) specifies the colour of the line for the series
                    - 'legend': The name of the series
            **kwargs: Other keys which should be applied to all series.
        """
        plots = []
        y_tooltips = []
        legend_entries = []
        for s in ys:
            series = copy(s)
            y = series.pop('y')
            series.update(kwargs)
            series_name = series.get('legend') or y
            y_tooltips.append((series_name, f"@{y}")) # Tool tips of form (title, @data_source_key)
            plot = self._figure.line(x=x, y=y, source=data_source, **series)
            legend_entries.append((series_name, [plot]))  # Associate legend entry with plot

            plots.append(plot)

        self._figure.legend.location = None
        self._figure.title.align = 'center'
        # Only need legend if more than one series
        if len(ys) > 1:
            legend = Legend(items=legend_entries, location=(0,0))
            legend.click_policy = 'mute'
            self._figure.add_layout(legend, 'right')

        # Create a hover tool
        x_tooltip = (self._figure.xaxis[0].axis_label or x, f"@{x}")
        tooltips = [x_tooltip] + y_tooltips  # Combine tooltips to get main list of tooltips for hover information
        hover_tool = HoverTool(
            renderers=[plots[0]],  # Apply HoverTool to just one line so that information appears in one box (the one
                                   # associated with that plot)
            tooltips=tooltips,
            mode='vline',
        )
        self._figure.add_tools(hover_tool)

        # Apply empty tool tip to all other lines so that they get selected when hovered but no information is displayed
        # for them. All information displayed in box for first line.
        self._figure.add_tools(HoverTool(renderers=plots[1:], mode='vline', tooltips=[]))
