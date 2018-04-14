from typing import List, Union

from bokeh.models import Tabs
from bokeh.plotting import Figure


class BaseBuilder:
    """
    Base class for building the charts for an analysis.
    """
    def build_chart(self, results: dict) -> Union[Figure, List[Figure], Tabs]:
        """
        Returns the figure to include in the report for a validation analysis.
        Args:
            results: The results of the validation analysis.

        Returns:
            The figure to include in the report for a validation analysis.
        """
        raise NotImplementedError