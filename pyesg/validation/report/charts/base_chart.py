from copy import copy

from bokeh.plotting import figure, Figure


class BaseChart:
    """
    Base class to create figures for charts.
    """
    def __init__(self, **kwargs):
        kwargs = copy(kwargs)  # Copy kwargs so we don't modify existing object
        height = kwargs.pop("height", 300)
        width = kwargs.pop("width", 600)
        self._figure = figure(toolbar_location=None, height=height, width=width, **kwargs)  # type: Figure

    @property
    def figure(self) -> Figure:
        """
        Returns the figure containing the plot.
        Returns:
            The figure containing the plot.
        """
        return self._figure
